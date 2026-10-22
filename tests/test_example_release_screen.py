"""Permit the named public tutorial without opening arbitrary host paths."""
import unittest
from pathlib import Path

from scripts.build_trial import reviewed_example_path, screen_content


class ExampleReleaseScreenTests(unittest.TestCase):
    def test_only_named_tutorial_resources_allow_the_synthetic_root(self):
        root = "C:" + "/CoGov"
        for name in ("docs/en/windows-example.md", "docs/zh-CN/windows-example.md", "docs/zh-TW/windows-example.md",
                     "examples/windows_quickstart/bootstrap.py"):
            for path in (root, root + "/runtime/Scripts/python.exe", root + "/control/"):
                with self.subTest(name=name, path=path):
                    self.assertTrue(reviewed_example_path(name, path))
                    screen_content({name: path.encode()})
        with self.assertRaises(RuntimeError):
            screen_content({"agct/core.py": root.encode()})

    def test_other_roots_and_escapes_remain_rejected(self):
        root = "C:" + "/CoGov"
        for path in (root + "Other/file.md", root + "/../private.md",
                     root + "/./private.md", root + "/control/../../private.md",
                     "D:" + "/CoGov", "C:" + "/Users/example/private.md"):
            with self.subTest(path=path), self.assertRaises(RuntimeError):
                screen_content({"docs/en/windows-example.md": path.encode()})

    def test_complete_quoted_paths_and_standalone_lines_are_allowed(self):
        root = "C:" + "/CoGov"
        path = root + "/runtime/Scripts/python.exe"
        for text in ("Use `" + path + "` now.", "& '" + path + "' -m agct",
                     'Run "' + path + '" next.', "  " + path + "  \r\n"):
            with self.subTest(text=text):
                screen_content({"docs/en/windows-example.md": text.encode()})

    def test_quoted_paths_are_checked_in_full_including_spaces_and_parentheses(self):
        root = "C:" + "/CoGov"
        for path in (root + "/with space/../../Users/example/private.md",
                     root + "/(scratch)/../../Users/example/private.md"):
            for quote in ('"', "'", "`"):
                with self.subTest(path=path, quote=quote), self.assertRaisesRegex(RuntimeError, "unreviewed_absolute_path"):
                    screen_content({"docs/en/windows-example.md": (quote + path + quote).encode()})

    def test_unquoted_paths_cannot_allow_a_truncated_prefix(self):
        root = "C:" + "/CoGov"
        for text in (root + "/with space/../../Users/example/private.md",
                     root + "/(scratch)/../../Users/example/private.md",
                     "Use " + root + "/control here.",
                     "Use " + root + "; this is an unquoted narrative path."):
            with self.subTest(text=text), self.assertRaisesRegex(RuntimeError, "unreviewed_absolute_path"):
                screen_content({"docs/en/windows-example.md": text.encode()})

    def test_secret_and_private_token_screens_still_apply_to_tutorial(self):
        root = "C:" + "/CoGov"
        with self.assertRaises(RuntimeError):
            screen_content({"docs/en/windows-example.md": (root + " PRIVATE_TOKEN").encode()},
                           ["PRIVATE_TOKEN"])
        with self.assertRaises(RuntimeError):
            screen_content({"docs/en/windows-example.md": (root + " sk-" + "a" * 40).encode()})

    def test_reviewed_image_cannot_be_replaced_or_allow_other_binary_assets(self):
        name = "docs/assets/workspace-sidebar-example.png"
        content = (Path(__file__).resolve().parents[1] / name).read_bytes()
        screen_content({name: content})
        with self.assertRaisesRegex(RuntimeError, "reviewed_asset_changed"):
            screen_content({name: content + b"unreviewed change"})
        with self.assertRaisesRegex(RuntimeError, "unexpected_binary"):
            screen_content({"docs/assets/unreviewed.png": content})


if __name__ == "__main__":
    unittest.main()
