import copy
import unittest

from quality_forms import validate_record


def example(**changes):
    record = {
        "id": "SYNTHETIC-001", "date": "2024-02-29", "area": "Training workshop",
        "severity": "minor", "description": "Fictional label alignment issue",
        "owner": "Example operator", "status": "open",
    }
    return {**record, **changes}


class QualityFormTests(unittest.TestCase):
    def test_valid_open_and_investigating(self):
        for state in ("open", "investigating"):
            self.assertEqual(validate_record(example(status=state)), [])

    def test_valid_resolved_and_closed(self):
        self.assertEqual(validate_record(example(status="resolved", resolution="Reprinted label")), [])
        self.assertEqual(validate_record(example(status="closed", resolution="Reprinted label", reviewer="Example reviewer")), [])

    def test_missing_fields_report_in_stable_contract_order(self):
        self.assertEqual(validate_record({}), [f"{field} is required" for field in ("id", "date", "area", "severity", "description", "owner", "status")])

    def test_invalid_fields_do_not_crash_or_mutate_input(self):
        for field in ("id", "date", "area", "severity", "description", "owner", "status"):
            for invalid in (None, False, 17, [], {}, "", "  "):
                record = example(**{field: invalid})
                before = copy.deepcopy(record)
                self.assertIn(f"{field} must be a nonempty string", validate_record(record))
                self.assertEqual(record, before)

    def test_non_object_payload(self):
        for value in ([], None, "record", 1):
            self.assertEqual(validate_record(value), ["record must be a JSON object"])

    def test_strict_calendar_dates(self):
        for invalid in ("2025-02-29", "2024-02-30", "2024-13-01", "2024-1-01", "20240229", " 2024-02-29", "2024-02-29T00:00:00", "0000-01-01"):
            self.assertIn("date must be a real calendar date in YYYY-MM-DD format", validate_record(example(date=invalid)))
        self.assertEqual(validate_record(example(date="2000-02-29")), [])

    def test_severity_enum_is_exact(self):
        for valid in ("minor", "major", "critical"):
            self.assertEqual(validate_record(example(severity=valid)), [])
        for invalid in ("Major", "warning", " minor "):
            self.assertIn("severity must be minor, major or critical", validate_record(example(severity=invalid)))

    def test_unknown_status(self):
        self.assertIn("status must be open, investigating, resolved or closed", validate_record(example(status="finished")))

    def test_resolution_required_for_resolved_and_closed(self):
        for state in ("resolved", "closed"):
            for value in (None, "", " "):
                self.assertIn(f"resolution is required when status is {state}", validate_record(example(status=state, resolution=value)))

    def test_closed_requires_reviewer(self):
        for reviewer in (None, "", "  "):
            self.assertIn("reviewer is required when status is closed", validate_record(example(status="closed", resolution="Corrected", reviewer=reviewer)))

    def test_optional_text_types(self):
        for field in ("resolution", "reviewer"):
            self.assertIn(f"{field} must be text when provided", validate_record(example(**{field: ["not text"]})))

    def test_unknown_fields_are_explicit_and_sorted(self):
        self.assertEqual(validate_record(example(zeta=1, alpha=2)), ["unknown field: alpha", "unknown field: zeta"])


if __name__ == "__main__":
    unittest.main()
