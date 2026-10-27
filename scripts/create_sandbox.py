"""Create new synthetic local repositories for agent and tester rehearsal."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from taskcarry.core import Core
from taskcarry.integration import Integration
from taskcarry.gitops import git, commit

SPEC = """# Synthetic quality management forms

This disposable, fictional workshop needs a small quality-record prototype.
It contains no real customer, medical, business or production records.

Record fields: id (nonempty string), date (YYYY-MM-DD), area (nonempty),
severity (minor/major/critical), description (nonempty), owner (nonempty),
status (open/investigating/resolved/closed), resolution (optional text),
reviewer (optional text). Resolved records require resolution; closed records
require resolution and reviewer. Unknown statuses and missing required fields
must produce understandable validation errors. No network services are required.

Schema worker: schemas/quality-record.schema.json, samples/valid.json,
samples/invalid.json. Deliver v1 then a cumulative v2 refining resolved/closed
conditions and sample coverage. Preserve history.

Service worker: quality_forms.py and tests/test_quality_forms.py. Python standard
library validation, deterministic errors, no server/database/dependency needed.

UI worker: web/index.html, web/app.js, web/style.css. Local form entry, visible
validation, a safe text-rendered record preview, no remote assets. Leave a small
unsubmitted UI improvement note and checkpoint it after stable delivery.

All workers continue the same task; stable stage delivery does not mean this
prototype has production acceptance. Use only generated example values.
"""


def create(destination):
    root = Path(destination).resolve()
    if root.exists() and any(root.iterdir()):
        raise ValueError("Sandbox destination must be absent or empty")
    root.mkdir(parents=True, exist_ok=True)
    baseline = root / "baseline"
    baseline.mkdir()
    git(baseline, "init", "-b", "main")
    git(baseline, "config", "user.name", "Synthetic Workshop")
    git(baseline, "config", "user.email", "workshop@example.invalid")
    (baseline / "SPEC.md").write_text(SPEC, encoding="utf-8")
    (baseline / ".gitignore").write_text("__pycache__/\n*.pyc\n.taskcarry/\n", encoding="utf-8")
    git(baseline, "add", "--", "SPEC.md", ".gitignore")
    git(baseline, "commit", "-m", "Create synthetic quality form exercise")
    project = root / "governance"
    Core.initialize(project, name="Synthetic quality workshop")
    (project / ".taskcarry" / "SYNTHETIC_TEST_ONLY").write_text("Generated material only\n", encoding="utf-8")
    engine = Integration(project)
    engine.workspace("baseline", baseline)
    manifest = {"synthetic": True, "project": str(project), "baseline": str(baseline), "base_commit": commit(baseline, "HEAD"), "workers": {}}
    for name in ("schema", "service", "ui"):
        workspace = root / "workers" / name
        workspace.parent.mkdir(exist_ok=True)
        git(root, "clone", "--no-hardlinks", str(baseline), str(workspace))
        git(workspace, "config", "user.name", "Synthetic " + name)
        git(workspace, "config", "user.email", name + "@example.invalid")
        engine.workspace(name, workspace)
        engine.core.task(name, title="Quality form " + name, workstream=name)
        manifest["workers"][name] = str(workspace)
    (root / "sandbox.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("destination")
    print(json.dumps(create(parser.parse_args().destination), ensure_ascii=False, indent=2))
