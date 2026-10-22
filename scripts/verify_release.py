"""Run the disposable test suite and emit portable, non-sensitive evidence."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class EvidenceResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.records.append({"test": test.id(), "outcome": "PASS"})

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.records.append({"test": test.id(), "outcome": "SKIP", "reason": reason})

    def addFailure(self, test, error):
        super().addFailure(test, error)
        self.records.append({"test": test.id(), "outcome": "FAIL"})

    def addError(self, test, error):
        super().addError(test, error)
        self.records.append({"test": test.id(), "outcome": "ERROR"})


def run(output):
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    result = unittest.TextTestRunner(verbosity=2, resultclass=EvidenceResult).run(suite)
    evidence = {"schema": "agct.test-evidence.v1", "recorded_at": datetime.now(timezone.utc).isoformat(),
                "platform": platform.system(), "python": platform.python_version(), "tests_run": result.testsRun,
                "passed": sum(x["outcome"] == "PASS" for x in result.records), "skipped": len(result.skipped),
                "failures": len(result.failures), "errors": len(result.errors), "successful": result.wasSuccessful(), "tests": result.records}
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    raise SystemExit(run(parser.parse_args().output))
