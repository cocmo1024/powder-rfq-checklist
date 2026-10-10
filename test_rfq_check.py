import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from rfq_check import FIELDS, check, read


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.data = {"fields": [{"id": field, "status": "confirmed",
            "requirement": "See project requirement revision A",
            "evidence": "Buyer specification revision A, section 4", "notes": ""}
            for field in FIELDS]}

    def test_complete_record_is_only_completeness(self):
        self.assertEqual(check(self.data), [])

    def test_missing_and_duplicate_are_not_silently_accepted(self):
        self.data["fields"][-1] = copy.deepcopy(self.data["fields"][0])
        issues = check(self.data)
        self.assertTrue(any("Duplicate" in x for x in issues))
        self.assertTrue(any("delivery_requirements: missing" in x for x in issues))

    def test_placeholders_and_blank_evidence(self):
        row = self.data["fields"][0]
        row.update(requirement="Oxygen limit TBD", evidence=" ")
        self.assertEqual(len(check(self.data)), 2)

    def test_pending_even_with_filled_text(self):
        self.data["fields"][0]["status"] = "pending"
        self.assertEqual(len(check(self.data)), 1)

    def test_not_applicable_needs_reason(self):
        row = self.data["fields"][0]
        row.update(status="not_applicable", requirement="", evidence="", notes="TBC")
        self.assertEqual(len(check(self.data)), 1)
        row["notes"] = "Buyer excludes this item in written scope revision A"
        self.assertEqual(check(self.data), [])

    def test_malformed_input(self):
        for data in ([], None, {"fields": 3}, {"fields": [3, {"id": []}]}):
            self.assertTrue(check(data))

    def test_unknown_fields_and_status(self):
        self.data["fields"].append({"id": "typo"})
        self.data["fields"][0]["status"] = "approved"
        self.assertEqual(len(check(self.data)), 2)

    def test_csv_and_json_templates_are_equivalent(self):
        root = Path(__file__).parent
        self.assertEqual(check(read(root / "rfq-template.csv")), check(read(root / "rfq-template.json")))
        self.assertEqual(len(check(read(root / "rfq-template.json"))), len(FIELDS))

    def test_cli_exit_and_never_material_accepted(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "rfq.json"
            path.write_text(json.dumps(self.data), encoding="utf-8")
            run = subprocess.run([sys.executable, str(Path(__file__).with_name("rfq_check.py")),
                                  str(path), "--json"], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0)
            self.assertFalse(json.loads(run.stdout)["material_accepted"])
            path.write_text("bad json", encoding="utf-8")
            invalid = subprocess.run([sys.executable, str(Path(__file__).with_name("rfq_check.py")),
                                      str(path)], capture_output=True, text=True)
            self.assertEqual(invalid.returncode, 2)


if __name__ == "__main__":
    unittest.main()
