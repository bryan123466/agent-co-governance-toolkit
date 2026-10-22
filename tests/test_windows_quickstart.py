"""Synthetic CLI bootstrap checks; never create the default example location."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from agct.api import invoke


SOURCE = Path(__file__).resolve().parents[1] / "examples/windows_quickstart/bootstrap.py"
SPEC = importlib.util.spec_from_file_location("windows_quickstart", SOURCE)
bootstrap = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bootstrap)


class WindowsQuickstartTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agct-quickstart-")
        self.root = Path(self.temp.name) / "new-project"

    def tearDown(self):
        self.temp.cleanup()

    def test_empty_control_is_reused_without_assigning_tasks(self):
        self.root.mkdir()
        (self.root / "control").mkdir()
        for name in ("toolkit", "runtime"):
            (self.root / name).mkdir()
            (self.root / name / "keep.txt").write_text("untouched", encoding="utf-8")
        result = bootstrap.generate(self.root)
        self.assertEqual("READY", result["status"])
        self.assertEqual(4, result["skills_installed"])
        self.assertFalse(result["mcp_activated"])
        self.assertFalse(result["automation_created"])
        self.assertTrue(result["reused_empty_control"])
        self.assertEqual(0, result["agent_count"])
        self.assertEqual(1, result["workspace_count"])
        self.assertEqual(0, result["tasks_created"])
        state = invoke(self.root / "control", "status")
        self.assertEqual({"baseline"}, {w["name"] for w in state["workspaces"]})
        self.assertEqual([], state["tasks"])
        self.assertEqual([], state["stages"])
        for workspace in [Path(result["baseline"]), *[Path(w["path"]) for w in result["workers"]]]:
            self.assertEqual("", bootstrap.git(workspace, "status", "--porcelain"))
            self.assertEqual(result["seed_commit"], bootstrap.git(workspace, "rev-parse", "HEAD"))
        self.assertEqual("codex/governance-baseline", bootstrap.git(Path(result["baseline"]), "branch", "--show-current"))
        for worker in result["workers"]:
            self.assertEqual(worker["branch"], bootstrap.git(Path(worker["path"]), "branch", "--show-current"))
        self.assertEqual({"README.md", "PROJECT_CONTEXT.md"}, set(bootstrap.git(self.root / "repository", "ls-files").splitlines()))
        local_config = bootstrap.git(self.root / "repository", "config", "--local", "--list")
        self.assertNotIn("user.name=", local_config)
        self.assertNotIn("user.email=", local_config)
        self.assertEqual("AGCT Bootstrap|bootstrap@example.invalid", bootstrap.git(self.root / "repository", "log", "-1", "--format=%an|%ae"))
        for name in ("toolkit", "runtime"):
            self.assertEqual("untouched", (self.root / name / "keep.txt").read_text(encoding="utf-8"))
        with self.assertRaisesRegex(ValueError, "existing target"):
            bootstrap.generate(self.root)
        self.assertEqual("READY", json.loads((self.root / "QUICKSTART.json").read_text())["status"])

    def test_optional_one_and_five_workers_need_explicit_task_registration(self):
        for count in (1, 5):
            with self.subTest(agents=count):
                root = self.root / str(count)
                result = bootstrap.generate(root, agents=count, name="My actual project")
                self.assertEqual(count, result["agent_count"])
                self.assertEqual(count + 1, result["workspace_count"])
                self.assertEqual("My actual project", result["name"])
                state = invoke(root / "control", "status")
                self.assertEqual([], state["tasks"])
                self.assertEqual({"baseline", *[f"agent-{n}" for n in range(1, count + 1)]}, {w["name"] for w in state["workspaces"]})
                for worker in result["workers"]:
                    self.assertEqual(worker["branch"], bootstrap.git(Path(worker["path"]), "branch", "--show-current"))
                    self.assertNotIn("task_id", worker)
                invoke(root / "control", "task", {"task_id": "USER-TASK", "title": "User-defined work", "workstream": "user-stream"})
                checkpoint = invoke(root / "control", "checkpoint", {"task_id": "USER-TASK", "workspace": "agent-1",
                                    "paths": ["PROJECT_CONTEXT.md"], "next_step": "Continue the user's defined project."})
                self.assertIn("checkpoint_id", checkpoint)

    def test_nonempty_control_including_governance_state_is_preserved(self):
        for name in ("notes.txt", ".agct"):
            with self.subTest(content=name):
                root = self.root / name.replace(".", "-")
                control = root / "control"
                control.mkdir(parents=True)
                existing = control / name
                existing.write_bytes(b"preserve existing control")
                with self.assertRaisesRegex(ValueError, "completely empty"):
                    bootstrap.generate(root)
                self.assertEqual(["control"], [p.name for p in root.iterdir()])
                self.assertEqual(b"preserve existing control", existing.read_bytes())

    def test_existing_target_refuses_before_other_writes(self):
        for name in ("control", "repository", "workspaces", "QUICKSTART.json"):
            with self.subTest(target=name):
                root = self.root / name.replace(".", "-")
                root.mkdir(parents=True)
                existing = root / name
                existing.write_bytes(b"preserve me")
                with self.assertRaisesRegex(ValueError, "existing target"):
                    bootstrap.generate(root)
                self.assertEqual([name], [p.name for p in root.iterdir()])
                self.assertEqual(b"preserve me", existing.read_bytes())

    def test_missing_git_does_not_create_root(self):
        with mock.patch.object(bootstrap.shutil, "which", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "Git must"):
                bootstrap.generate(self.root)
        self.assertFalse(self.root.exists())

    def test_interruption_keeps_evidence_and_rejects_retry(self):
        with mock.patch.object(bootstrap, "git", side_effect=RuntimeError("synthetic Git interruption")):
            with self.assertRaisesRegex(RuntimeError, "synthetic Git interruption"):
                bootstrap.generate(self.root)
        self.assertTrue((self.root / "repository/PROJECT_CONTEXT.md").is_file())
        self.assertEqual("INCOMPLETE", json.loads((self.root / "QUICKSTART.json").read_text())["status"])
        with self.assertRaises(ValueError):
            bootstrap.generate(self.root)

    def test_cli_uses_explicit_isolated_root(self):
        environment = {**os.environ, "PYTHONPATH": str(SOURCE.parents[2])}
        result = subprocess.run([sys.executable, str(SOURCE), "--root", str(self.root), "--agents", "1", "--name", "CLI project"],
                                capture_output=True, text=True, encoding="utf-8", timeout=90, env=environment)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("READY", payload["status"])
        self.assertEqual(str(self.root.resolve()), payload["root"])
        self.assertEqual(1, payload["agent_count"])
        self.assertEqual(0, payload["tasks_created"])
        self.assertEqual("CLI project", payload["name"])

    def test_invalid_arguments_do_not_create_a_root(self):
        for agents in (-1, True, False, "1", 1.5):
            with self.subTest(agents=agents), self.assertRaises(ValueError):
                bootstrap.generate(self.root, agents=agents)
        for name in ("", "\n", "Project\nInjected", "x" * 121):
            with self.subTest(name=name), self.assertRaises(ValueError):
                bootstrap.generate(self.root, name=name)
        self.assertFalse(self.root.exists())


if __name__ == "__main__":
    unittest.main()
