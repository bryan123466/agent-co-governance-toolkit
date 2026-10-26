"""Synthetic end-to-end governance lifecycles with real, isolated Git worktrees.

These tests exercise project-local integration assets, not Codex scheduling,
native model decisions, or hot replacement of an already running MCP process.
"""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from agct.core import Core
from agct.gitops import commit, git, out
from agct.integration import Integration
from agct.setup import configure, skill_sources
from agct.store import GovernanceError


class GovernanceLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agct-lifecycle-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.control = self.root / "control"
        Core.initialize(self.control, name="Synthetic collaborative project")
        self.core = Core(self.control)
        self.engine = Integration(self.control)
        self.baseline = self.root / "baseline"
        self.baseline.mkdir()
        git(self.baseline, "init", "-b", "main")
        git(self.baseline, "config", "core.autocrlf", "false")
        self.start = self.write_commit(self.baseline, {
            "README.md": "Synthetic collaborative project\n",
            "form.txt": "name\nstatus\n",
            "rules.txt": "revision one\n",
            ".gitignore": ".agct/\n",
        }, "Synthetic common baseline")
        self.engine.workspace("baseline", self.baseline)
        self.workers = {}
        for number in range(1, 4):
            name = "agent-" + str(number)
            path = self.root / name
            git(self.baseline, "worktree", "add", "-b", name, str(path), self.start)
            self.engine.workspace(name, path)
            self.workers[name] = path
            self.assertEqual(commit(path, "HEAD"), self.start)
        for task_id in ("forms", "research", "instructions"):
            self.core.task(task_id, title="Synthetic " + task_id)

    def write_commit(self, workspace, changes, message="Synthetic delivery"):
        for name, content in changes.items():
            target = workspace / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
        git(workspace, "add", "--", *changes)
        git(workspace, "commit", "-m", message)
        return commit(workspace, "HEAD")

    def submit(self, task_id, name, changes, stage_id, **relation):
        tip = self.write_commit(self.workers[name], changes)
        return self.engine.submit(task_id, name, tip, self.start, list(changes),
                                  stage_id=stage_id, **relation)["stage"]

    def git_layers(self, workspace):
        """Observe exact index bytes and file layers without refreshing the index."""
        tracked = git(workspace, "ls-files", "--cached", "-z").stdout
        untracked = git(workspace, "ls-files", "--others", "--exclude-standard", "-z").stdout
        names = {name.decode("utf-8") for name in (tracked + untracked).split(b"\0") if name}
        index = Path(out(workspace, "rev-parse", "--git-path", "index"))
        if not index.is_absolute():
            index = workspace / index
        return {
            "head": commit(workspace, "HEAD"),
            "tree": out(workspace, "rev-parse", "HEAD^{tree}"),
            "staged_entries": git(workspace, "ls-files", "--stage", "-z").stdout,
            "staged_form": git(workspace, "show", ":form.txt").stdout,
            "untracked": untracked,
            "files": {name: (workspace / name).read_bytes()
                      if (workspace / name).is_file() else None for name in names},
            "index_bytes": index.read_bytes(),
        }

    def pause_research(self):
        worker = self.workers["agent-2"]
        (worker / "form.txt").write_bytes(b"name\nstatus\nstaged research\n")
        git(worker, "add", "--", "form.txt")
        (worker / "form.txt").write_bytes(b"name\nstatus\nstaged research\nunresolved draft\n")
        (worker / "notes.bin").write_bytes(b"\x00\xffsynthetic unfinished evidence\x01")
        return self.core.checkpoint("research", worker, ["form.txt", "notes.bin"],
                                    "Continue the unresolved research question", paused=True)

    def test_three_workspaces_keep_pause_and_receive_latest_plus_independent(self):
        checkpoint = self.pause_research()
        paused_before = self.git_layers(self.workers["agent-2"])
        self.assertFalse(checkpoint["delivery"])
        self.assertEqual(self.core.store.get("tasks", "research")["state"], "paused")

        self.submit("forms", "agent-1", {"form.txt": "name\nstatus\nreviewer\n"}, "v1")
        self.submit("forms", "agent-1", {"form.txt": "name\nstatus\nreviewer\nresolution\n"},
                    "v2", relation="cumulative", supersedes=["v1"])
        latest = b"name\nstatus\nreviewer\nresolution\napprover\n"
        self.submit("forms", "agent-1", {"form.txt": latest}, "v3",
                    relation="cumulative", supersedes=["v2"])
        self.submit("instructions", "agent-3", {"rules.txt": "Independent operating instructions\n"},
                    "independent-guide")
        # Later WIP must not replace the already frozen third version.
        (self.workers["agent-1"] / "form.txt").write_bytes(latest + b"unfinished fourth version\n")
        workers_before = {name: self.git_layers(path) for name, path in self.workers.items()}
        plan = self.engine.reconcile("baseline")["plan"]
        self.assertEqual(set(plan["stage_ids"]), {"v3", "independent-guide"})
        result = self.engine.reconcile("baseline", True, plan["plan_id"])
        self.assertEqual(result["status"], "COMPLETE")
        self.assertEqual((self.baseline / "form.txt").read_bytes(), latest)
        self.assertEqual((self.baseline / "rules.txt").read_bytes(), b"Independent operating instructions\n")
        self.assertEqual(out(self.baseline, "rev-list", "--count", "HEAD"), "3")
        for stage_id in ("v1", "v2"):
            self.assertEqual(self.core.store.get("stages", stage_id)["status"], "SUPERSEDED")
        for stage_id in ("v3", "independent-guide"):
            self.assertEqual(self.core.store.get("stages", stage_id)["status"], "COMMITTED")
        self.assertFalse(any(stage["task_id"] == "research" for stage in self.core.store.list("stages")))
        self.assertEqual(self.engine.reconcile("baseline")["plan"]["stage_ids"], [])
        self.assertEqual(self.git_layers(self.workers["agent-2"]), paused_before)
        self.assertEqual({name: self.git_layers(path) for name, path in self.workers.items()}, workers_before)
        self.assertEqual(self.core.store.get("checkpoints", checkpoint["checkpoint_id"]), checkpoint)
        self.assertEqual(self.core.store.get("tasks", "research")["state"], "paused")
        self.assertNotEqual(self.core.store.get("tasks", "forms")["state"], "complete")
        restored = self.root / "restored-research"
        self.core.restore(checkpoint["checkpoint_id"], restored)
        self.assertEqual((restored / "form.txt").read_bytes(), paused_before["files"]["form.txt"])
        self.assertEqual(git(restored, "show", ":form.txt").stdout, paused_before["staged_form"])
        self.assertEqual((restored / "notes.bin").read_bytes(), paused_before["files"]["notes.bin"])

    def test_interrupted_effect_uses_existing_experience_without_duplicate_commit(self):
        self.submit("forms", "agent-1", {"form.txt": "name\nstatus\nreviewed\n"}, "recoverable-stage")
        plan = self.engine.reconcile("baseline")["plan"]
        (self.control / ".agct" / "SYNTHETIC_TEST_ONLY").write_text("synthetic", encoding="utf-8")
        workers_before = {name: self.git_layers(path) for name, path in self.workers.items()}
        with patch.dict(os.environ, {"AGCT_TEST_FAULTS": "1"}):
            with self.assertRaises(GovernanceError) as caught:
                self.engine.reconcile("baseline", True, plan["plan_id"], fault="after_effect")
        self.assertEqual(caught.exception.code, "INJECTED_INTERRUPTION")
        effect_head = commit(self.baseline, "HEAD")
        self.assertNotEqual(effect_head, self.start)
        self.assertEqual((self.baseline / "form.txt").read_bytes(), b"name\nstatus\nreviewed\n")
        self.assertEqual(out(self.baseline, "rev-list", "--count", "HEAD"), "2")
        self.assertNotEqual(self.core.store.get("stages", "recoverable-stage")["status"], "COMMITTED")
        # Reopening the controller proves recovery comes from durable evidence,
        # not in-memory knowledge retained by the interrupted invocation.
        resumed = Integration(self.control)
        recovered = resumed.reconcile("baseline", True, plan["plan_id"])
        self.assertEqual(recovered["status"], "COMPLETE")
        self.assertTrue(recovered["results"][0]["recovered"])
        self.assertEqual(recovered["results"][0]["experience_rule"], "receipt-recovery-v1")
        self.assertEqual(self.core.store.get("stages", "recoverable-stage")["status"], "COMMITTED")
        applied = [event for event in self.core.store.events() if event["kind"] == "experience_applied"]
        self.assertEqual(len(applied), 1)
        self.assertTrue(applied[0]["payload"]["effect_verified"])
        self.assertEqual(applied[0]["payload"]["rule_id"], "receipt-recovery-v1")
        self.assertTrue(resumed.reconcile("baseline", True, plan["plan_id"])["reused"])
        self.assertEqual(commit(self.baseline, "HEAD"), effect_head)
        self.assertEqual(out(self.baseline, "rev-list", "--count", "HEAD"), "2")
        self.assertEqual(len([event for event in self.core.store.events()
                              if event["kind"] == "experience_applied"]), 1)
        self.assertEqual({name: self.git_layers(path) for name, path in self.workers.items()}, workers_before)

    def test_project_skill_refresh_preserves_business_layers_and_task_memory(self):
        checkpoint = self.pause_research()
        for name in ("agent-1", "agent-3"):
            worker = self.workers[name]
            (worker / "form.txt").write_bytes((name + " staged work\n").encode())
            git(worker, "add", "--", "form.txt")
            (worker / "form.txt").write_bytes((name + " unstaged continuation\n").encode())
            (worker / "draft.bin").write_bytes(b"\x00\xfe" + name.encode())
        before = {name: self.git_layers(path) for name, path in
                  {"baseline": self.baseline, **self.workers}.items()}
        collections = ("tasks", "checkpoints", "stages", "operations", "experience", "workspaces")
        records_before = self.core.store.snapshot(collections)
        events_before = self.core.store.events()
        configure(self.control, "install")
        sources = skill_sources()
        replacements = []
        for source in sources:
            destination = self.root / "synthetic-skill-release" / source.parent.name / "SKILL.md"
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source.read_bytes() + b"\nSynthetic lifecycle verification revision.\n")
            replacements.append(destination)
        with patch("agct.setup.skill_sources", return_value=replacements):
            preview = configure(self.control, "preview")
            self.assertFalse(preview["conflicts"])
            configure(self.control, "install")
            for source in replacements:
                installed = self.control / ".agents" / "skills" / source.parent.name / "SKILL.md"
                self.assertEqual(installed.read_bytes(), source.read_bytes())
            repeated = configure(self.control, "preview")
            self.assertTrue(all(row["action"] == "unchanged" for row in repeated["files"]))
            configure(self.control, "install")
        self.assertEqual({name: self.git_layers(path) for name, path in
                          {"baseline": self.baseline, **self.workers}.items()}, before)
        self.assertEqual(self.core.store.snapshot(collections), records_before)
        self.assertEqual(self.core.store.events(), events_before)
        reopened = Core(self.control)
        self.assertEqual(reopened.store.snapshot(collections), records_before)
        self.assertEqual(reopened.store.get("tasks", "research")["latest_checkpoint"], checkpoint["checkpoint_id"])
        restored = self.root / "restored-after-skill-update"
        reopened.restore(checkpoint["checkpoint_id"], restored)
        self.assertEqual((restored / "notes.bin").read_bytes(), before["agent-2"]["files"]["notes.bin"])
        self.assertEqual(git(restored, "show", ":form.txt").stdout, before["agent-2"]["staged_form"])


if __name__ == "__main__":
    unittest.main()
