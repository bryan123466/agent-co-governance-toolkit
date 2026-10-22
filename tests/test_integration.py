"""Real Git integration/recovery tests; all repositories are generated locally."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from agct.core import Core
from agct.integration import Integration
from agct.gitops import git, out, fingerprint, commit, ancestor
from agct.store import GovernanceError


class GitFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agct-integration-")
        self.root = Path(self.temp.name)
        self.control = self.root / "control"
        Core.initialize(self.control, name="Synthetic quality system")
        self.core = Core(self.control)
        self.engine = Integration(self.control)
        self.base = self.root / "baseline"
        self.base.mkdir()
        git(self.base, "init", "-b", "main")
        git(self.base, "config", "user.name", "Synthetic Tester")
        git(self.base, "config", "user.email", "tester@example.invalid")
        (self.base / "README.md").write_text("Synthetic quality system\n", encoding="utf-8")
        (self.base / "form.txt").write_text("name\nstatus\n", encoding="utf-8")
        (self.base / "rules.txt").write_text("revision one\n", encoding="utf-8")
        git(self.base, "add", "--", "README.md", "form.txt", "rules.txt")
        git(self.base, "commit", "-m", "Synthetic starting point")
        self.start = commit(self.base, "HEAD")
        self.worker = self.root / "worker"
        git(self.root, "clone", "--no-hardlinks", str(self.base), str(self.worker))
        git(self.worker, "config", "user.name", "Synthetic Worker")
        git(self.worker, "config", "user.email", "worker@example.invalid")
        self.engine.workspace("baseline", self.base)
        self.engine.workspace("worker", self.worker)
        self.core.task("forms", title="Quality form workflow")

    def tearDown(self):
        # SQLite connections are short lived; no active children remain here.
        self.temp.cleanup()

    def write_commit(self, path, changes, message="Synthetic stage"):
        for name, value in changes.items():
            f = path / name
            f.parent.mkdir(parents=True, exist_ok=True)
            if value is None:
                f.unlink()
            elif isinstance(value, bytes):
                f.write_bytes(value)
            else:
                f.write_text(value, encoding="utf-8")
        git(path, "add", "--", *changes)
        git(path, "commit", "-m", message)
        return commit(path, "HEAD")

    def delivery(self, changes=None, **kwargs):
        changes = changes or {"form.txt": "name\nstatus\nreviewer\n"}
        tip = self.write_commit(self.worker, changes)
        return self.engine.submit("forms", "worker", tip, kwargs.pop("base", self.start), list(changes), **kwargs)["stage"]

    def plan(self):
        return self.engine.reconcile("baseline")["plan"]["plan_id"]

    def execute(self, plan=None, **kwargs):
        return self.engine.reconcile("baseline", True, plan or self.plan(), **kwargs)


class ReceiveTests(GitFixture):
    def test_true_integration_and_idempotent_receipt(self):
        stage = self.delivery()
        pid = self.plan()
        result = self.execute(pid)
        head = commit(self.base, "HEAD")
        self.assertEqual(result["status"], "COMPLETE")
        self.assertIn("reviewer", (self.base / "form.txt").read_text())
        self.assertTrue(result["results"][0]["integration_verified"])
        self.assertTrue(self.execute(pid)["reused"])
        self.assertEqual(commit(self.base, "HEAD"), head)
        self.assertEqual(self.engine.store.get("stages", stage["stage_id"])["status"], "COMMITTED")

    def test_local_commit_without_submit_is_not_backlog(self):
        self.write_commit(self.worker, {"draft.txt": "unfinished"})
        self.core.task("forms", state="paused")
        result = self.engine.reconcile("baseline")
        self.assertEqual(result["plan"]["stage_ids"], [])
        self.assertEqual(self.engine.store.list("stages"), [])

    def test_exact_manifest_rejects_omitted_file(self):
        tip = self.write_commit(self.worker, {"form.txt": "new", "other.txt": "other"})
        with self.assertRaises(GovernanceError) as e:
            self.engine.submit("forms", "worker", tip, self.start, ["form.txt"])
        self.assertEqual(e.exception.code, "MANIFEST_MISMATCH")
        self.assertEqual(commit(self.base, "HEAD"), self.start)

    def test_mutable_workspace_does_not_change_frozen_delivery(self):
        self.delivery()
        (self.worker / "form.txt").write_text("new unfinished work")
        self.execute()
        self.assertEqual((self.base / "form.txt").read_text(), "name\nstatus\nreviewer\n")
        self.assertEqual((self.worker / "form.txt").read_text(), "new unfinished work")

    def test_cumulative_latest_replaces_unreceived_stages(self):
        first = self.delivery(stage_id="v1")
        second = self.delivery({"form.txt": "name\nstatus\nreviewer\nresolution\n"}, stage_id="v2", relation="cumulative", supersedes=[first["stage_id"]])
        self.assertEqual(self.engine.reconcile("baseline")["plan"]["stage_ids"], [second["stage_id"]])
        self.execute()
        self.assertEqual(self.engine.store.get("stages", "v1")["status"], "SUPERSEDED")
        self.assertEqual(out(self.base, "rev-list", "--count", "HEAD"), "2")

    def test_cumulative_after_received_uses_previous_source_base(self):
        self.delivery(stage_id="v1")
        self.execute()
        self.delivery({"form.txt": "name\nstatus\nreviewer\nresolution\n"}, stage_id="v2", relation="cumulative", supersedes=["v1"])
        self.execute()
        self.assertIn("resolution", (self.base / "form.txt").read_text())

    def test_three_version_chain_retires_all_historical_pending(self):
        self.delivery(stage_id="v1")
        self.delivery({"form.txt": "name\nstatus\nreviewer\nresolution\n"}, stage_id="v2", relation="cumulative", supersedes=["v1"])
        self.delivery({"form.txt": "name\nstatus\nreviewer\nresolution\napprover\n"}, stage_id="v3", relation="cumulative", supersedes=["v2"])
        self.execute()
        self.assertEqual(self.engine.store.get("stages", "v1")["status"], "SUPERSEDED")
        self.assertEqual(self.engine.store.get("stages", "v2")["status"], "SUPERSEDED")
        self.assertEqual(self.engine.reconcile("baseline")["plan"]["stage_ids"], [])

    def test_unrelated_task_cannot_be_superseded(self):
        first = self.delivery(stage_id="v1")
        self.core.task("another", title="Different workstream")
        tip = self.write_commit(self.worker, {"form.txt": "next"})
        with self.assertRaises(GovernanceError) as e:
            self.engine.submit("another", "worker", tip, self.start, ["form.txt"], relation="cumulative", supersedes=[first["stage_id"]])
        self.assertEqual(e.exception.code, "INVALID_PREDECESSOR")

    def test_stale_plan_and_baseline_wip_preserved(self):
        self.delivery()
        pid = self.plan()
        self.write_commit(self.base, {"unrelated.txt": "baseline moved"})
        with self.assertRaises(GovernanceError) as e:
            self.execute(pid)
        self.assertEqual(e.exception.code, "STALE_BASELINE")
        (self.base / "draft.txt").write_text("keep me")
        with self.assertRaises(GovernanceError) as e:
            self.execute()
        self.assertEqual(e.exception.code, "BASELINE_WIP")
        self.assertEqual((self.base / "draft.txt").read_text(), "keep me")

    def test_conflict_does_not_block_independent_delivery(self):
        self.delivery({"form.txt": "worker change\n"})
        self.write_commit(self.base, {"form.txt": "baseline change\n"})
        self.core.task("reports", title="Independent report")
        tip = self.write_commit(self.worker, {"report.txt": "independent"})
        parent = out(self.worker, "rev-parse", "HEAD^")
        self.engine.submit("reports", "worker", tip, parent, ["report.txt"])
        result = self.execute()
        self.assertEqual(result["status"], "ACTION_REQUIRED")
        self.assertEqual((self.base / "form.txt").read_text(), "baseline change\n")
        self.assertEqual((self.base / "report.txt").read_text(), "independent")
        again = self.execute()
        self.assertEqual(again["status"], "ACTION_REQUIRED")
        self.assertEqual(len(again["remaining"]), 1)

    def test_binary_and_deletion_receive(self):
        self.delivery({"rules.txt": None, "asset.bin": b"\x00\x01\x02\xff"})
        self.execute()
        self.assertFalse((self.base / "rules.txt").exists())
        self.assertEqual((self.base / "asset.bin").read_bytes(), b"\x00\x01\x02\xff")

    def test_fault_disabled_outside_marked_tests(self):
        self.delivery()
        with self.assertRaises(GovernanceError) as e:
            self.execute(fault="after_effect")
        self.assertEqual(e.exception.code, "FAULT_INJECTION_DISABLED")
        self.assertEqual(commit(self.base, "HEAD"), self.start)

    def test_interruption_and_experience_recovery_without_duplicate_effect(self):
        self.delivery()
        pid = self.plan()
        (self.control / ".agct" / "SYNTHETIC_TEST_ONLY").write_text("synthetic")
        with patch.dict(os.environ, {"AGCT_TEST_FAULTS": "1"}):
            with self.assertRaises(GovernanceError) as e:
                self.execute(pid, fault="after_effect")
        self.assertEqual(e.exception.code, "INJECTED_INTERRUPTION")
        head = commit(self.base, "HEAD")
        result = self.execute(pid)
        self.assertTrue(result["results"][0]["recovered"])
        self.assertEqual(commit(self.base, "HEAD"), head)
        self.assertEqual(out(self.base, "rev-list", "--count", "HEAD"), "2")

    def test_outdated_experience_does_not_authorize_recovery(self):
        self.core.experience("receipt-recovery-v1", "EFFECT_PRESENT_RECEIPT_MISSING", "reconcile", "verify_and_finalize", version="0")
        self.delivery()
        pid = self.plan()
        (self.control / ".agct" / "SYNTHETIC_TEST_ONLY").write_text("synthetic")
        with patch.dict(os.environ, {"AGCT_TEST_FAULTS": "1"}):
            with self.assertRaises(GovernanceError):
                self.execute(pid, fault="after_effect")
        head = commit(self.base, "HEAD")
        with self.assertRaises(GovernanceError) as e:
            self.execute(pid)
        self.assertEqual(e.exception.code, "EXPERIENCE_REVIEW_REQUIRED")
        self.assertEqual(commit(self.base, "HEAD"), head)
        self.core.experience("receipt-recovery-v1", "EFFECT_PRESENT_RECEIPT_MISSING", "reconcile", "verify_and_finalize")
        self.assertEqual(self.execute(pid)["status"], "COMPLETE")


class AdoptTests(GitFixture):
    def dirty_worker(self):
        local = self.write_commit(self.worker, {"local.txt": "private local progress"})
        (self.worker / "form.txt").write_text("name\nstatus\nstaged\n")
        git(self.worker, "add", "--", "form.txt")
        (self.worker / "form.txt").write_text("name\nstatus\nstaged\nunstaged\n")
        (self.worker / "notes.bin").write_bytes(b"\0unfinished\xff")
        (self.worker / "rules.txt").unlink()
        return local

    def test_adoption_preserves_local_commits_and_all_git_layers(self):
        local = self.dirty_worker()
        staged = git(self.worker, "show", ":form.txt").stdout
        self.write_commit(self.base, {"shared.txt": "public update"})
        pid = self.engine.adopt("worker", "baseline")["plan"]["plan_id"]
        result = self.engine.adopt("worker", "baseline", True, pid)
        self.assertEqual(result["status"], "ADOPTED")
        self.assertTrue(result["wip_verified"])
        self.assertTrue(ancestor(self.worker, local, commit(self.worker, "HEAD")))
        self.assertEqual(git(self.worker, "show", ":form.txt").stdout, staged)
        self.assertIn("unstaged", (self.worker / "form.txt").read_text())
        self.assertFalse((self.worker / "rules.txt").exists())
        self.assertEqual((self.worker / "notes.bin").read_bytes(), b"\0unfinished\xff")
        self.assertEqual((self.worker / "shared.txt").read_text(), "public update")
        before = fingerprint(self.worker)
        self.assertTrue(self.engine.adopt("worker", "baseline", True, pid)["reused"])
        self.assertEqual(fingerprint(self.worker), before)

    def test_wip_conflict_retains_original_state(self):
        (self.worker / "form.txt").write_text("private incompatible content\n")
        original = fingerprint(self.worker)
        self.write_commit(self.base, {"form.txt": "public incompatible content\n"})
        pid = self.engine.adopt("worker", "baseline")["plan"]["plan_id"]
        with self.assertRaises(GovernanceError) as e:
            self.engine.adopt("worker", "baseline", True, pid)
        self.assertEqual(e.exception.code, "WIP_CONFLICT")
        self.assertEqual(fingerprint(self.worker), original)

    def test_staged_change_cancelled_in_worktree_is_still_backed_up(self):
        original = (self.worker / "form.txt").read_bytes()
        (self.worker / "form.txt").write_text("staged-only change\n")
        git(self.worker, "add", "--", "form.txt")
        (self.worker / "form.txt").write_bytes(original)
        self.write_commit(self.base, {"shared.txt": "update"})
        pid = self.engine.adopt("worker", "baseline")["plan"]["plan_id"]
        result = self.engine.adopt("worker", "baseline", True, pid)
        self.assertIsNotNone(result["checkpoint_id"])
        self.assertEqual(git(self.worker, "show", ":form.txt").stdout, b"staged-only change\n")
        self.assertEqual((self.worker / "form.txt").read_bytes(), original)

    def test_interrupted_adoption_resumes_exact_stash(self):
        self.dirty_worker()
        self.write_commit(self.base, {"shared.txt": "public update"})
        pid = self.engine.adopt("worker", "baseline")["plan"]["plan_id"]
        (self.control / ".agct" / "SYNTHETIC_TEST_ONLY").write_text("synthetic")
        with patch.dict(os.environ, {"AGCT_TEST_FAULTS": "1"}):
            with self.assertRaises(GovernanceError):
                self.engine.adopt("worker", "baseline", True, pid, fault="after_adopt")
        result = self.engine.adopt("worker", "baseline", True, pid)
        self.assertTrue(result["wip_verified"])
        self.assertIn("unstaged", (self.worker / "form.txt").read_text())
        self.assertEqual(len(out(self.worker, "stash", "list").splitlines()), 1)


if __name__ == "__main__":
    unittest.main()
