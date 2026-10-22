"""Additive project-scoped Codex setup. Never edits global or live Codex config."""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import tempfile


class SetupError(ValueError):
    def __init__(self, code, message, details=None):
        super().__init__(message)
        self.code, self.message, self.details = code, message, details


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_target(root, relative):
    path = root / relative
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise SetupError("SETUP_PATH_ESCAPE", "Managed path is outside the project")
    current = path
    while current != root:
        if is_link(current):
            raise SetupError("SETUP_LINK", "Setup refuses links in managed paths", {"path": relative})
        current = current.parent
    if not path.resolve().is_relative_to(root):
        raise SetupError("SETUP_PATH_ESCAPE", "Managed path escapes the project")
    return path


def is_link(path):
    if path.is_symlink():
        return True
    try:
        return bool(getattr(path.lstat(), "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))
    except FileNotFoundError:
        return False


def skill_sources():
    package = Path(__file__).resolve().parent
    for candidate in (package / "skill_data", package.parent / "skills"):
        if candidate.is_dir():
            sources = sorted(candidate.glob("*/SKILL.md"))
            if len(sources) == 4:
                return sources
    raise SetupError("SKILLS_NOT_PACKAGED", "Four public skills were not found in the installed package")


def planned_files(root):
    files = {}
    for source in skill_sources():
        files[f".agents/skills/{source.parent.name}/SKILL.md"] = source.read_bytes()
    package_parent = Path(__file__).resolve().parent.parent
    quote = lambda value: json.dumps(str(value), ensure_ascii=False)
    args = ["-m", "agct", "--project", str(root), "mcp"]
    fragment = (
        "# Generated project-specific MCP fragment. This is NOT loaded automatically.\n"
        "# Review and add this section to the appropriate Codex configuration.\n"
        "# Do not copy this fragment to another machine: regenerate it there.\n"
        "[mcp_servers.agct]\n"
        f"command = {quote(sys.executable)}\n"
        f"args = {json.dumps(args, ensure_ascii=False)}\n"
        "\n[mcp_servers.agct.env]\n"
        f"PYTHONPATH = {quote(package_parent)}\n"
        "PYTHONUTF8 = \"1\"\n"
    )
    files[".agct/codex.mcp.toml"] = fragment.encode("utf-8")
    return files


def read_manifest(root):
    path = safe_target(root, ".agct/setup-manifest.json")
    if not path.exists():
        return {"format": 1, "files": {}}
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise SetupError("SETUP_MANIFEST_INVALID", "Setup manifest cannot be read") from exc
    if not isinstance(result, dict) or result.get("format") != 1 or not isinstance(result.get("files"), dict):
        raise SetupError("SETUP_MANIFEST_INVALID", "Setup manifest has an unsupported format")
    for name, value in result["files"].items():
        if not isinstance(name, str) or not isinstance(value, str) or len(value) != 64:
            raise SetupError("SETUP_MANIFEST_INVALID", "Invalid managed file record")
        if not (name == ".agct/codex.mcp.toml" or (name.startswith(".agents/skills/agct-") and name.endswith("/SKILL.md") and len(Path(name).parts) == 4)):
            raise SetupError("SETUP_MANIFEST_INVALID", "Manifest includes a path outside the managed setup scope")
        safe_target(root, name)
    return result


@contextmanager
def setup_lock(root):
    directory = safe_target(root, ".agct")
    directory.mkdir(parents=True, exist_ok=True)
    path = safe_target(root, ".agct/setup.lock")
    stream = path.open("a+b")
    try:
        if os.name == "nt":
            import msvcrt
            stream.seek(0, os.SEEK_END)
            if stream.tell() == 0:
                stream.write(b"0")
                stream.flush()
            stream.seek(0)
            try:
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise SetupError("SETUP_BUSY", "Another setup process holds the project setup lock") from exc
        else:
            import fcntl
            try:
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise SetupError("SETUP_BUSY", "Another setup process holds the project setup lock") from exc
        yield
    finally:
        stream.close()


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".agct-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def preview(root, files, manifest):
    changes, conflicts = [], []
    for name, content in files.items():
        path = safe_target(root, name)
        current = digest(path.read_bytes()) if path.is_file() else None
        if path.exists() and not path.is_file():
            conflicts.append({"path": name, "reason": "not_a_regular_file"})
        elif path.exists() and current != manifest["files"].get(name):
            conflicts.append({"path": name, "reason": "unmanaged_or_modified"})
        else:
            changes.append({"path": name, "action": "unchanged" if current == digest(content) else ("update" if path.exists() else "create"), "sha256": digest(content)})
    return {"mode": "preview", "project": str(root), "files": changes, "conflicts": conflicts,
            "activation": "The TOML fragment is not active configuration. Review it and explicitly configure Codex; generated skills are project scoped.",
            "global_config_changed": False, "agents_md_changed": False}


def configure(project, mode="preview"):
    if mode not in {"preview", "install", "uninstall"}:
        raise SetupError("SETUP_MODE", "mode must be preview, install or uninstall")
    supplied = Path(project).absolute()
    if is_link(supplied):
        raise SetupError("SETUP_LINK", "Setup requires a concrete project directory")
    root = supplied.resolve()
    if not root.is_dir():
        raise SetupError("PROJECT_NOT_FOUND", "Setup requires an existing project directory")
    if mode == "preview":
        return preview(root, planned_files(root), read_manifest(root))
    with setup_lock(root):
        manifest = read_manifest(root)
        manifest_path = safe_target(root, ".agct/setup-manifest.json")
        if mode == "uninstall":
            removed, preserved, remaining = [], [], {}
            for name, original in manifest["files"].items():
                path = safe_target(root, name)
                if not path.exists():
                    continue
                if path.is_file() and digest(path.read_bytes()) == original:
                    path.unlink()
                    removed.append(name)
                else:
                    preserved.append(name)
                    remaining[name] = original
            if remaining:
                atomic_write(manifest_path, json.dumps({"format": 1, "files": remaining}, indent=2).encode("utf-8"))
            elif manifest_path.exists():
                manifest_path.unlink()
            return {"mode": mode, "removed": removed, "preserved_modified": preserved,
                    "global_config_changed": False, "agents_md_changed": False,
                    "note": "Any configuration section manually activated in Codex remains user managed. Governance state and user files are retained."}
        files = planned_files(root)
        result = preview(root, files, manifest)
        if result["conflicts"]:
            raise SetupError("SETUP_CONFLICT", "Existing unmanaged or changed files are preserved", result)
        # Persist each completed file independently. An interruption between file and
        # manifest writes is a safe conflict on retry, never permission to overwrite.
        for name, content in files.items():
            path = safe_target(root, name)
            if path.exists() and digest(path.read_bytes()) != manifest["files"].get(name):
                raise SetupError("SETUP_CONFLICT", "Managed file changed after preview", {"path": name})
            atomic_write(path, content)
            manifest["files"][name] = digest(content)
            atomic_write(manifest_path, json.dumps(manifest, indent=2).encode("utf-8"))
        result["mode"] = "install"
        return result
