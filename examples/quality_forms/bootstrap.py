"""Create only a new fictional local Git scenario; never inspect an existing project."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess


def git(repository: Path, *arguments: str) -> str:
    environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    environment.update(GIT_TERMINAL_PROMPT="0", GIT_CONFIG_NOSYSTEM="1")
    result = subprocess.run(
        ["git", "-c", "init.templateDir=", "-c", "core.hooksPath=" + os.devnull,
         "-c", "commit.gpgSign=false", "-c", "core.autocrlf=false", "-C", str(repository), *arguments],
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
        env=environment,
        timeout=60,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def generate(destination: Path) -> dict:
    destination = destination.expanduser().resolve()
    if destination.exists():
        raise ValueError("Destination must not exist; choose a new disposable directory.")
    if shutil.which("git") is None:
        raise RuntimeError("Git is required to create this example.")
    fixture = Path(__file__).resolve().parent / "fixture"
    # No caller-supplied source directory is read or copied.
    destination.mkdir(parents=True, exist_ok=False)
    baseline = destination / "baseline"
    shutil.copytree(fixture, baseline)
    control = destination / "control"
    control.mkdir()
    requests = destination / "requests"
    requests.mkdir()
    git(baseline, "init", "-b", "main")
    git(baseline, "config", "user.name", "Synthetic Example")
    git(baseline, "config", "user.email", "example@example.invalid")
    git(baseline, "add", "--", "requirements.md", "forms/inspection.csv", "review/review-checklist.md", "quality/corrective-actions.csv")
    git(baseline, "commit", "-m", "Create fictional quality workflow fixture")
    base = git(baseline, "rev-parse", "HEAD")

    def request(name: str, data: dict) -> None:
        (requests / f"{name}.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    request("init", {"name": "Inspection and issue-tracking example"})
    request("workspace-baseline", {"name": "baseline", "path": str(baseline)})
    files = {
        "forms": "forms/inspection.csv",
        "review": "review/review-checklist.md",
        "quality": "quality/corrective-actions.csv",
    }
    workers = {}
    (destination / "workers").mkdir()
    for name, relative in files.items():
        worker = destination / "workers" / name
        git(baseline, "worktree", "add", "-b", f"worker/{name}", str(worker), "main")
        task_id = f"TASK-{name.upper()}"
        workers[name] = str(worker)
        request(f"workspace-{name}", {"name": name, "path": str(worker)})
        request(f"task-{name}", {"task_id": task_id, "title": f"Fictional {name} work", "workstream": name, "state": "active"})
        request(f"checkpoint-{name}", {"task_id": task_id, "workspace": name, "paths": [relative], "next_step": "Review the assigned worker brief and continue the fictional example.", "paused": True})
        request(f"submit-{name}-template", {"task_id": task_id, "workspace": name, "base": base, "commit": "REPLACE_WITH_YOUR_NEW_COMMIT", "paths": [relative], "stage_id": f"{name}-stage-1", "relation": "independent"})
    request("reconcile-plan", {"baseline": "baseline"})
    result = {"synthetic": True, "destination": str(destination), "control": str(control), "baseline": str(baseline), "baseline_commit": base, "workers": workers, "requests": str(requests), "note": "Governance has not been initialized or executed; follow the example README or project getting-started guide."}
    (destination / "SCENARIO.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True)
    arguments = parser.parse_args()
    try:
        print(json.dumps(generate(Path(arguments.destination)), ensure_ascii=False, indent=2))
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
