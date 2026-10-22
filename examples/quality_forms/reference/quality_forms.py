"""Validation for a fictional quality-form prototype; standard library only."""
from datetime import date
import json
from pathlib import Path
import re
import sys

REQUIRED = ("id", "date", "area", "severity", "description", "owner", "status")
OPTIONAL = ("resolution", "reviewer")
SEVERITIES = ("minor", "major", "critical")
STATUSES = ("open", "investigating", "resolved", "closed")


def validate_record(record):
    """Return deterministic human-readable errors without changing the record."""
    if not isinstance(record, dict):
        return ["record must be a JSON object"]
    errors = []
    for field in REQUIRED:
        if field not in record:
            errors.append(f"{field} is required")
        elif not isinstance(record[field], str) or not record[field].strip():
            errors.append(f"{field} must be a nonempty string")
    for field in OPTIONAL:
        if field in record and not isinstance(record[field], str):
            errors.append(f"{field} must be text when provided")
    for field in sorted(set(record) - set(REQUIRED) - set(OPTIONAL), key=str):
        errors.append(f"unknown field: {field}")

    value = record.get("date")
    if isinstance(value, str) and value.strip():
        try:
            if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
                raise ValueError()
            date.fromisoformat(value)
        except ValueError:
            errors.append("date must be a real calendar date in YYYY-MM-DD format")

    severity = record.get("severity")
    if isinstance(severity, str) and severity.strip() and severity not in SEVERITIES:
        errors.append("severity must be minor, major or critical")
    status = record.get("status")
    if isinstance(status, str) and status.strip() and status not in STATUSES:
        errors.append("status must be open, investigating, resolved or closed")
    if status in ("resolved", "closed") and not (
        isinstance(record.get("resolution"), str) and record["resolution"].strip()
    ):
        errors.append(f"resolution is required when status is {status}")
    if status == "closed" and not (
        isinstance(record.get("reviewer"), str) and record["reviewer"].strip()
    ):
        errors.append("reviewer is required when status is closed")
    return errors


def main(argv=None):
    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) != 1:
        print("Usage: python quality_forms.py <record.json>", file=sys.stderr)
        return 2
    try:
        record = json.loads(Path(arguments[0]).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        print(json.dumps({"valid": False, "errors": [f"Cannot read JSON record: {exc}"]}))
        return 2
    errors = validate_record(record)
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
