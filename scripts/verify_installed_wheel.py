"""Validate a built wheel in a disposable installation, not from the checkout."""
import argparse
import json
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def run(directory, output=None):
    wheels = list(Path(directory).resolve().glob("taskcarry-*.whl"))
    if len(wheels) != 1:
        raise SystemExit("Use a directory containing exactly one TaskCarry wheel")
    os.environ["TASKCARRY_TEST_WHEEL"] = str(wheels[0])
    # Import after setting the environment so unittest's skip condition is real.
    suite = unittest.defaultTestLoader.loadTestsFromName(
        "tests.test_release_contract.InstalledWheelContractTests")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    evidence = {"schema": "taskcarry.installed-wheel-evidence.v1", "wheel": wheels[0].name,
                "tests_run": result.testsRun, "failures": len(result.failures),
                "errors": len(result.errors), "skipped": len(result.skipped),
                "successful": result.wasSuccessful() and result.testsRun == 1 and not result.skipped}
    if output:
        Path(output).write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    return 0 if evidence["successful"] else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    raise SystemExit(run(args.directory, args.output))
