"""Check RFQ handoff completeness, never material acceptance. Python 3.10+."""
import argparse
import csv
import json
import re
from pathlib import Path

FIELDS = (
    "alloy_and_specification", "process_and_machine", "particle_size_distribution",
    "chemistry_and_interstitials", "flow_and_density", "powder_condition",
    "lot_traceability", "required_documents", "sampling_and_acceptance",
    "quantity_and_packaging", "delivery_requirements",
)
PLACEHOLDER = re.compile(r"\b(tbd|tbc|todo|unknown|pending|to be confirmed|to be agreed)\b", re.I)


def substantive(value):
    return isinstance(value, str) and bool(value.strip()) and not PLACEHOLDER.search(value)


def check(data):
    """Return review issues. Text content is not technically qualified by this check."""
    if not isinstance(data, dict) or not isinstance(data.get("fields"), list):
        return ["Input must be an object containing a fields array."]
    issues, by_id = [], {}
    for index, row in enumerate(data["fields"]):
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            issues.append(f"Row {index + 1}: expected an object with a string id.")
            continue
        key = row["id"]
        if key not in FIELDS:
            issues.append(f"Unknown field: {key}.")
            continue
        if key in by_id:
            issues.append(f"Duplicate field: {key}.")
            continue
        by_id[key] = row
    for key in FIELDS:
        row = by_id.get(key)
        if row is None:
            issues.append(f"{key}: missing field.")
            continue
        status = row.get("status")
        if status not in ("confirmed", "pending", "not_applicable"):
            issues.append(f"{key}: status must be confirmed, pending or not_applicable.")
        elif status == "pending":
            issues.append(f"{key}: pending; record the owner and next action in notes.")
        elif status == "not_applicable":
            if not substantive(row.get("notes")):
                issues.append(f"{key}: not_applicable requires a meaningful reason in notes.")
        else:
            if not substantive(row.get("requirement")):
                issues.append(f"{key}: confirmed requires a non-placeholder requirement.")
            if not substantive(row.get("evidence")):
                issues.append(f"{key}: confirmed requires a non-placeholder evidence reference.")
    return issues


def read(path):
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as stream:
            return {"fields": list(csv.DictReader(stream))}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, help="RFQ JSON or CSV")
    parser.add_argument("--json", action="store_true", help="Machine-readable report")
    args = parser.parse_args()
    try:
        issues = check(read(args.file))
    except (OSError, UnicodeError, ValueError, csv.Error) as exc:
        parser.exit(2, f"Cannot read RFQ: {exc}\n")
    report = {"review_items": issues, "handoff_fields_recorded": not issues,
              "material_accepted": False,
              "note": "Completeness only. Evidence, limits, methods and suitability need human review."}
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Review items:" if issues else "Handoff fields recorded; human technical review still required.")
        for item in issues:
            print(f"- {item}")
        print(report["note"])
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
