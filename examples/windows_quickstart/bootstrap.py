"""Create a neutral new-project scaffold without inventing tasks or roles.

Run with the Python environment that already has TaskCarry installed. The default
layout is `C:/TaskCarry`; --root selects a separate disposable validation location.
An existing completely empty control directory is allowed. Existing toolkit/runtime
directories are left alone. No remote, scheduled task,
active Codex configuration, or global Git configuration is created or changed.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys


CONTEXT = "# Project context\n\n" \
    "## Goal\nNot defined yet. Record the user's actual goal before assigning work.\n\n" \
    "## Scope and constraints\nNot defined yet. Preserve existing decisions and materials.\n\n" \
    "## Tasks and responsibilities\nNo tasks or professional roles have been assigned.\n\n" \
    "## Next step\nDiscuss the real project in the governance chat, then create explicit tasks and workspaces.\n"


def no_links(path: Path) -> None:
    """Reject link/reparse ancestors before resolving a requested destination."""
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError(f"Links are not supported in the quickstart path: {part}")
        try:
            attributes = getattr(part.lstat(), "st_file_attributes", 0)
        except FileNotFoundError:
            continue
        if attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0):
            raise ValueError(f"Reparse points are not supported in the quickstart path: {part}")


def git(repository: Path, *arguments: str) -> str:
    environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    environment.update(GIT_TERMINAL_PROMPT="0", GIT_CONFIG_NOSYSTEM="1")
    result = subprocess.run(
        ["git", "-c", "init.templateDir=", "-c", "core.hooksPath=" + os.devnull,
         "-c", "commit.gpgSign=false", "-c", "core.autocrlf=false", "-C", str(repository), *arguments],
        env=environment, capture_output=True, text=True, encoding="utf-8", timeout=60,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Git failed")
    return result.stdout.strip()


def generate(root: Path, agents: int = 0, name: str = "Project") -> dict:
    # Import the installed toolkit; do not install dependencies or alter sys.path.
    from taskcarry.api import invoke
    from taskcarry.setup import configure, skill_sources

    if type(agents) is not int or agents < 0:
        raise ValueError("agents must be a nonnegative integer.")
    if not isinstance(name, str) or not name.strip() or len(name) > 120 or any(ord(c) < 32 for c in name):
        raise ValueError("name must be a nonempty single-line project name of at most 120 characters.")
    name = name.strip()
    requested = root.expanduser().absolute()
    no_links(requested)
    root = requested.resolve()
    if root.exists() and not root.is_dir():
        raise ValueError("The quickstart root must be a directory.")
    targets = [root / name for name in ("control", "repository", "workspaces", "QUICKSTART.json")]
    control = targets[0]
    no_links(control)
    reused_control = control.exists()
    if reused_control and (not control.is_dir() or any(control.iterdir())):
        raise ValueError(f"Refusing an existing target: control must be completely empty: {control}")
    for target in targets[1:]:
        if os.path.lexists(target):
            raise ValueError(f"Refusing an existing target; nothing was replaced: {target}")
    if shutil.which("git") is None:
        raise RuntimeError("Git must be available on PATH before creating the project.")
    skill_sources()  # Confirm the four skills are available before creating anything.

    root.mkdir(parents=True, exist_ok=True)
    marker = root / "QUICKSTART.json"
    # Exclusive creation also makes a repeated/concurrent bootstrap refuse the root.
    with marker.open("x", encoding="utf-8") as stream:
        json.dump({"status": "PREPARING", "kind": "project-bootstrap", "root": str(root)}, stream)
        stream.write("\n")

    try:
        control, repository, workspaces = targets[:3]
        if reused_control:
            no_links(control)
            if not control.is_dir() or any(control.iterdir()):
                raise ValueError("The previously empty control directory changed; nothing in it was replaced.")
        else:
            control.mkdir(exist_ok=False)
        for directory in (repository, workspaces):
            directory.mkdir(exist_ok=False)
        files = {"README.md": f"# {name}\n\nA new project managed with TaskCarry.\n\n"
                 "The initial commit contains only this neutral scaffold.\n"
                 "Define the actual goal and scope in PROJECT_CONTEXT.md using the user's instructions.\n",
                 "PROJECT_CONTEXT.md": CONTEXT}
        for relative, content in files.items():
            path = repository / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(content)
        git(repository, "init", "-b", "main")
        git(repository, "config", "--local", "core.autocrlf", "false")
        git(repository, "add", "--", *files)
        git(repository, "-c", "user.name=TaskCarry Bootstrap", "-c", "user.email=bootstrap@example.invalid",
            "commit", "-m", "Create neutral project scaffold")
        seed = git(repository, "rev-parse", "HEAD")
        baseline = workspaces / "baseline"
        git(repository, "worktree", "add", "-b", "codex/governance-baseline", str(baseline), seed)
        invoke(control, "init", {"name": name})
        invoke(control, "workspace", {"name": "baseline", "path": str(baseline)})
        workers = []
        for number in range(1, agents + 1):
            worker_name = f"agent-{number}"
            path, branch = workspaces / worker_name, f"codex/{worker_name}"
            git(repository, "worktree", "add", "-b", branch, str(path), seed)
            invoke(control, "workspace", {"name": worker_name, "path": str(path)})
            workers.append({"name": worker_name, "path": str(path), "branch": branch})
        setup = configure(control, mode="install")
        rows = ["# Project workspace map", "", f"Python: `{sys.executable}`",
                f"Control: `{control}`", f"Initial commit: `{seed}`", "",
                "The baseline is integration-only. Workers use the same CONTROL.",
                "Create task IDs and responsibilities from the user's actual project before checkpoint or submit.",
                "The initial commit uses a temporary TaskCarry Bootstrap identity; no Git user identity was saved.",
                "Professional commits must use the user's configured Git identity.",
                "No MCP connection or automation has been activated.", "",
                "| Workspace | Branch | Responsibility |", "|---|---|---|",
                "| baseline | codex/governance-baseline | Integration only |"]
        rows.extend(f"| {w['name']} | {w['branch']} | Not assigned |" for w in workers)
        (control / "PROJECT_MAP.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
        result = {"status": "READY", "kind": "project-bootstrap", "name": name, "root": str(root), "python": sys.executable,
                  "control": str(control), "repository": str(repository), "baseline": str(baseline),
                  "baseline_branch": "codex/governance-baseline", "seed_commit": seed, "workers": workers,
                  "agent_count": agents, "workspace_count": agents + 1, "tasks_created": 0,
                  "reused_empty_control": reused_control, "git_user_identity_saved": False,
                  "skills_installed": len(list((control / ".agents/skills").glob("*/SKILL.md"))),
                  "setup_mode": setup["mode"], "mcp_activated": False, "automation_created": False,
                  "remote_created": False, "note": "Neutral scaffold only. Define real goals and tasks before delivery; no stage has been submitted or received."}
        marker.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return result
    except Exception as exc:
        # Retain partial files and evidence. Never clean up work or retry over them.
        marker.write_text(json.dumps({"status": "INCOMPLETE", "kind": "project-bootstrap", "root": str(root),
                                      "error": str(exc), "note": "Partial files retained. Do not rerun over this root."},
                                     ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("C:/TaskCarry"))
    parser.add_argument("--agents", type=int, default=0,
                        help="Pre-create N worker workspaces without assigning tasks; N must be nonnegative (default: 0)")
    parser.add_argument("--name", default="Project", help="Actual project name (default: Project)")
    args = parser.parse_args()
    try:
        print(json.dumps(generate(args.root, agents=args.agents, name=args.name), ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
