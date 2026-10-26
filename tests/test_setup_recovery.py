"""Observable installation recovery using synthetic project directories only."""
from pathlib import Path
import errno
import json
import tempfile
import tomllib
import unittest
from unittest.mock import patch

import agct
from agct import setup


class SetupRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()

    def tearDown(self):
        self.temporary.cleanup()

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
                for p in self.root.rglob("*") if p.is_file()}

    def fail_after_first_file(self, **kwargs):
        original = setup.atomic_write
        target = next(iter(setup.planned_files(self.root)))

        def interrupt(path, content):
            original(path, content)
            if path == self.root / target:
                raise RuntimeError("synthetic interruption after file effect")

        with patch.object(setup, "atomic_write", side_effect=interrupt):
            with self.assertRaisesRegex(RuntimeError, "synthetic interruption"):
                setup.configure(self.root, mode="install", **kwargs)
        return self.root / target

    def test_resume_after_file_effect_does_not_rewrite_completed_file(self):
        target = self.fail_after_first_file()
        original = (target.read_bytes(), target.stat().st_mtime_ns)
        self.assertFalse((self.root / ".agct/setup-manifest.json").exists())
        pending = json.loads((self.root / ".agct/setup-intent.json").read_text())
        self.assertIsNone(pending["files"][target.relative_to(self.root).as_posix()]["before"])
        result = setup.configure(self.root, mode="install")
        self.assertTrue(result["resumed"])
        self.assertEqual(result["files_written"], len(result["files"]) - 1)
        self.assertEqual((target.read_bytes(), target.stat().st_mtime_ns), original)
        self.assertFalse((self.root / ".agct/setup-intent.json").exists())
        self.assertTrue(setup.runtime_info(self.root)["managed_files_match"])

    def test_crash_before_manifest_only_records_completed_files_on_resume(self):
        original = setup.atomic_write

        def interrupt(path, content):
            if path.name == "setup-manifest.json":
                raise RuntimeError("synthetic interruption before manifest")
            original(path, content)

        with patch.object(setup, "atomic_write", side_effect=interrupt):
            with self.assertRaises(RuntimeError):
                setup.configure(self.root, mode="install")
        saved = {name: (self.root / name).stat().st_mtime_ns for name in setup.planned_files(self.root)}
        result = setup.configure(self.root, mode="install")
        self.assertEqual(result["files_written"], 0)
        self.assertTrue(result["manifest_written"])
        self.assertEqual(saved, {name: (self.root / name).stat().st_mtime_ns for name in saved})

    def test_crash_after_manifest_only_removes_completed_intent(self):
        original = setup.atomic_write

        def interrupt(path, content):
            original(path, content)
            if path.name == "setup-manifest.json":
                raise RuntimeError("synthetic interruption after manifest")

        with patch.object(setup, "atomic_write", side_effect=interrupt):
            with self.assertRaises(RuntimeError):
                setup.configure(self.root, mode="install")
        manifest = self.root / ".agct/setup-manifest.json"
        before = (manifest.read_bytes(), manifest.stat().st_mtime_ns)
        with patch.object(setup, "atomic_write", side_effect=AssertionError("No file rewrite expected")):
            result = setup.configure(self.root, mode="install")
        self.assertEqual(result["files_written"], 0)
        self.assertFalse(result["manifest_written"])
        self.assertEqual((manifest.read_bytes(), manifest.stat().st_mtime_ns), before)

    def test_modified_completed_file_is_preserved_and_not_adopted(self):
        target = self.fail_after_first_file()
        target.write_text("User revision after interrupted setup", encoding="utf-8")
        before = self.snapshot()
        with self.assertRaises(setup.SetupError) as failure:
            setup.configure(self.root, mode="install")
        self.assertEqual(failure.exception.code, "SETUP_CONFLICT")
        self.assertEqual(before, self.snapshot())

    def test_unmanaged_file_equal_to_release_is_still_not_owned(self):
        name, content = next(iter(setup.planned_files(self.root).items()))
        path = self.root / name
        path.parent.mkdir(parents=True)
        path.write_bytes(content)
        with self.assertRaises(setup.SetupError) as failure:
            setup.configure(self.root, mode="install")
        self.assertEqual(failure.exception.code, "SETUP_CONFLICT")
        self.assertFalse((self.root / ".agct/setup-intent.json").exists())
        self.assertEqual(path.read_bytes(), content)

    def test_changed_package_version_cannot_resume_pending_install(self):
        self.fail_after_first_file()
        before = self.snapshot()
        with patch.object(agct, "__version__", agct.__version__ + ".different"):
            with self.assertRaises(setup.SetupError) as failure:
                setup.configure(self.root, mode="install")
        self.assertEqual(failure.exception.code, "SETUP_PENDING_SOURCE_CHANGED")
        self.assertEqual(before, self.snapshot())

    def test_changed_generated_candidate_cannot_resume_pending_install(self):
        self.fail_after_first_file()
        changed = setup.planned_files(self.root)
        name = next(iter(changed))
        changed[name] += b"\nNew candidate instructions\n"
        before = self.snapshot()
        with patch.object(setup, "planned_files", return_value=changed):
            with self.assertRaises(setup.SetupError) as failure:
                setup.configure(self.root, mode="install")
        self.assertEqual(failure.exception.code, "SETUP_PENDING_SOURCE_CHANGED")
        self.assertEqual(before, self.snapshot())

    def test_interrupted_update_keeps_the_existing_installation_identity(self):
        setup.configure(self.root, mode="install")
        manifest_path = self.root / ".agct/setup-manifest.json"
        previous = json.loads(manifest_path.read_text())
        updated = setup.planned_files(self.root)
        name = next(iter(updated))
        updated[name] += b"\nUpdated public instructions\n"
        original = setup.atomic_write

        def interrupt(path, content):
            original(path, content)
            if path == self.root / name:
                raise RuntimeError("synthetic update interruption")

        with patch.object(setup, "planned_files", return_value=updated):
            with patch.object(setup, "atomic_write", side_effect=interrupt):
                with self.assertRaises(RuntimeError):
                    setup.configure(self.root, mode="install")
            self.assertEqual(json.loads(manifest_path.read_text()), previous)
            result = setup.configure(self.root, mode="install")
        current = json.loads(manifest_path.read_text())
        self.assertTrue(result["resumed"])
        self.assertEqual(result["files_written"], 0)
        self.assertEqual(current["installation_id"], previous["installation_id"])
        self.assertEqual(current["files"][name], setup.digest(updated[name]))

    def test_package_changes_during_install_leave_a_pending_record(self):
        original = setup.loaded_runtime
        first = original()
        different = dict(first, source_sha256="0" * 64)
        with patch.object(setup, "loaded_runtime", side_effect=[first, different]):
            with self.assertRaises(setup.SetupError) as failure:
                setup.configure(self.root, mode="install")
        self.assertEqual(failure.exception.code, "SETUP_PENDING_SOURCE_CHANGED")
        self.assertTrue((self.root / ".agct/setup-intent.json").exists())
        self.assertFalse((self.root / ".agct/setup-manifest.json").exists())
        self.assertEqual(setup.configure(self.root, mode="install")["files_written"], 0)

    def test_pending_preview_and_diagnostics_are_read_only(self):
        self.fail_after_first_file(server_name="project_one")
        before = self.snapshot()
        preview = setup.configure(self.root)
        diagnostic = setup.runtime_info(self.root)
        self.assertTrue(preview["pending_installation"])
        self.assertFalse(preview["conflicts"])
        self.assertEqual(preview["server_name"], "project_one")
        self.assertEqual(diagnostic["setup_status"], "pending")
        self.assertEqual(diagnostic["loaded_runtime"]["version"], agct.__version__)
        self.assertTrue(diagnostic["pending_source_matches_disk"])
        self.assertNotIn("pending_source_matches_loaded", diagnostic)
        self.assertFalse(diagnostic["host_loading_verified"])
        self.assertEqual(before, self.snapshot())

    def test_fresh_preview_and_diagnostics_create_no_metadata(self):
        self.assertEqual(setup.runtime_info(self.root)["setup_status"], "not_installed")
        setup.configure(self.root)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_diagnostic_fingerprint_attests_disk_not_loaded_process_code(self):
        setup.configure(self.root, mode="install")
        before = self.snapshot()
        info = setup.runtime_info(self.root)
        self.assertTrue(info["managed_runtime_matches_disk"])
        self.assertNotIn("managed_runtime_matches_loaded", info)
        for observation in (info, info["loaded_runtime"]):
            self.assertEqual(observation["source_fingerprint_scope"], "on_disk")
            self.assertFalse(observation["loaded_code_verified"])
            self.assertTrue(observation["requires_restart_after_package_change"])
        self.assertFalse(info["host_loading_verified"])
        self.assertFalse(info["package_upgrade_performed"])
        self.assertEqual(before, self.snapshot())

    def test_source_read_failure_is_a_specific_read_only_diagnostic(self):
        setup.configure(self.root, mode="install")
        before = self.snapshot()
        package = Path(setup.__file__).resolve().parent
        original = Path.read_bytes

        def deny_source(path):
            if path.parent == package and path.suffix == ".py":
                raise PermissionError(errno.EACCES, "synthetic source read denied", str(path))
            return original(path)

        with patch.object(Path, "read_bytes", new=deny_source):
            info = setup.runtime_info(self.root)
        self.assertEqual(info["setup_status"], "unavailable")
        self.assertEqual(info["error"]["type"], "PermissionError")
        self.assertEqual(info["error"]["errno"], errno.EACCES)
        self.assertEqual(Path(info["error"]["filename"]).parent, package)
        self.assertIn("synthetic source read denied", info["error"]["message"])
        self.assertIsNone(info["loaded_runtime"])
        self.assertIsNone(info["managed_runtime_matches_disk"])
        self.assertFalse(info["loaded_code_verified"])
        self.assertEqual(before, self.snapshot())

    def test_changed_disk_source_does_not_claim_loaded_code_or_upgrade(self):
        setup.configure(self.root, mode="install")
        before = self.snapshot()
        initial = setup.runtime_info(self.root)
        source = Path(setup.__file__).resolve()
        original = Path.read_bytes

        def changed_source(path):
            payload = original(path)
            return payload + b"\n# synthetic disk revision\n" if path == source else payload

        with patch.object(Path, "read_bytes", new=changed_source):
            info = setup.runtime_info(self.root)
        self.assertEqual(info["loaded_runtime"]["version"], agct.__version__)
        self.assertNotEqual(info["loaded_runtime"]["source_sha256"], initial["loaded_runtime"]["source_sha256"])
        self.assertFalse(info["managed_runtime_matches_disk"])
        self.assertFalse(info["loaded_code_verified"])
        self.assertTrue(info["requires_restart_after_package_change"])
        self.assertFalse(info["package_upgrade_performed"])
        self.assertEqual(before, self.snapshot())

    def test_repeated_install_writes_no_identical_bytes(self):
        setup.configure(self.root, mode="install")
        before = self.snapshot()
        with patch.object(setup, "atomic_write", side_effect=AssertionError("No writes expected")):
            result = setup.configure(self.root, mode="install")
        self.assertEqual(result["files_written"], 0)
        self.assertFalse(result["manifest_written"])
        self.assertEqual(before, self.snapshot())

    def test_legacy_manifest_upgrade_preserves_files_and_then_is_idempotent(self):
        setup.configure(self.root, mode="install")
        path = self.root / ".agct/setup-manifest.json"
        manifest = json.loads(path.read_text())
        path.write_text(json.dumps({"format": 1, "files": manifest["files"]}), encoding="utf-8")
        self.assertIsNone(setup.runtime_info(self.root)["managed_setup_version"])
        result = setup.configure(self.root, mode="install")
        self.assertEqual(result["files_written"], 0)
        updated = json.loads(path.read_text())
        self.assertEqual(updated["files"], manifest["files"])
        self.assertEqual(updated["runtime"]["version"], agct.__version__)
        self.assertEqual(setup.configure(self.root, mode="install")["files_written"], 0)

    def test_server_names_persist_and_keep_two_projects_distinct(self):
        second = self.root / "second-project"
        second.mkdir()
        setup.configure(self.root, mode="install", server_name="agct_core")
        setup.configure(second, mode="install", server_name="agct-public")
        for project, name in ((self.root, "agct_core"), (second, "agct-public")):
            result = setup.configure(project, mode="install")
            self.assertEqual(result["server_name"], name)
            config = tomllib.loads((project / ".agct/codex.mcp.toml").read_text())
            self.assertEqual(list(config["mcp_servers"]), [name])
            self.assertIn(str(project), config["mcp_servers"][name]["args"])
            self.assertFalse((project / ".codex/config.toml").exists())

    def test_explicit_rename_updates_only_the_fragment(self):
        setup.configure(self.root, mode="install")
        result = setup.configure(self.root, mode="install", server_name="new_name")
        self.assertEqual(result["files_written"], 1)
        self.assertEqual(setup.configure(self.root)["server_name"], "new_name")

    def test_invalid_names_cannot_create_configuration(self):
        for name in ("", "x.y", "a\nb", "../escape", "a\"b", "a b", "1name", "a" * 65, 42):
            with self.subTest(name=name), self.assertRaises(setup.SetupError):
                setup.configure(self.root, mode="install", server_name=name)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_pending_install_cannot_switch_server_name_or_uninstall(self):
        self.fail_after_first_file(server_name="original")
        before = self.snapshot()
        for options, code in (({"mode": "install", "server_name": "different"}, "SETUP_PENDING_SOURCE_CHANGED"),
                              ({"mode": "uninstall"}, "SETUP_PENDING")):
            with self.assertRaises(setup.SetupError) as failure:
                setup.configure(self.root, **options)
            self.assertEqual(failure.exception.code, code)
        self.assertEqual(before, self.snapshot())

    def test_manifest_change_during_pending_install_is_not_overwritten(self):
        self.fail_after_first_file()
        path = self.root / ".agct/setup-manifest.json"
        path.write_text(json.dumps({"format": 1, "files": {}}), encoding="utf-8")
        before = self.snapshot()
        with self.assertRaises(setup.SetupError) as failure:
            setup.configure(self.root, mode="install")
        self.assertEqual(failure.exception.code, "SETUP_MANIFEST_CHANGED")
        self.assertEqual(before, self.snapshot())

    def test_diagnostic_detects_user_changes_without_writing(self):
        setup.configure(self.root, mode="install")
        target = self.root / ".agct/codex.mcp.toml"
        target.write_text("# user customization", encoding="utf-8")
        before = self.snapshot()
        info = setup.runtime_info(self.root)
        self.assertEqual(info["setup_status"], "modified")
        self.assertFalse(info["managed_files_match"])
        self.assertFalse(info["generated_files_match"])
        self.assertFalse(info["package_upgrade_performed"])
        self.assertEqual(before, self.snapshot())

    def test_invalid_intent_is_reported_without_repair(self):
        self.fail_after_first_file()
        path = self.root / ".agct/setup-intent.json"
        content = json.loads(path.read_text())
        content["installation_id"] = "0" * 32
        path.write_text(json.dumps(content), encoding="utf-8")
        before = self.snapshot()
        self.assertEqual(setup.runtime_info(self.root)["error"]["code"], "SETUP_INTENT_INVALID")
        with self.assertRaises(setup.SetupError):
            setup.configure(self.root)
        self.assertEqual(before, self.snapshot())

    def test_copied_intent_does_not_authorize_another_project(self):
        self.fail_after_first_file()
        other = self.root / "other"
        (other / ".agct").mkdir(parents=True)
        intent = (self.root / ".agct/setup-intent.json").read_bytes()
        (other / ".agct/setup-intent.json").write_bytes(intent)
        with self.assertRaises(setup.SetupError) as failure:
            setup.configure(other, mode="install")
        self.assertEqual(failure.exception.code, "SETUP_INTENT_INVALID")
        self.assertFalse((other / ".agents").exists())

    def test_user_write_after_intent_is_not_overwritten(self):
        original = setup.atomic_write
        target = self.root / next(iter(setup.planned_files(self.root)))

        def user_write(path, content):
            original(path, content)
            if path.name == "setup-intent.json":
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("Concurrent user file", encoding="utf-8")

        with patch.object(setup, "atomic_write", side_effect=user_write):
            with self.assertRaises(setup.SetupError) as failure:
                setup.configure(self.root, mode="install")
        self.assertEqual(failure.exception.code, "SETUP_CONFLICT")
        self.assertEqual(target.read_text(), "Concurrent user file")
        self.assertFalse((self.root / ".agct/setup-manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
