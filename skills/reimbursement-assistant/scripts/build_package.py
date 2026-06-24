import argparse
import shutil
from pathlib import Path

from lib_reimbursement import category_label, read_json, safe_filename, write_csv, write_json


FIELDS = [
    "included",
    "date",
    "merchant",
    "amount",
    "category",
    "invoice_number",
    "evidence_type",
    "source_file",
    "confidence",
    "suggested_action",
    "reason",
    "warnings",
]


def flatten(record):
    row = dict(record)
    row["warnings"] = ";".join(record.get("warnings") or [])
    return row


def copy_sources(records, out_dir):
    attachment_root = Path(out_dir) / "attachments"
    copied = []
    for record in records:
        source = Path(record.get("source_file") or "")
        if not source.is_file():
            continue
        category = record.get("category") or "unclassified"
        folder = attachment_root / safe_filename(f"{category}_{category_label(category)}")
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / safe_filename(source.name)
        if target.exists():
            target = folder / f"{target.stem}_{record.get('id', '')[:6]}{target.suffix}"
        shutil.copy2(source, target)
        copied.append({"record_id": record.get("id"), "source": str(source), "target": str(target)})
    return copied


def build(input_json, materials_json, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    data = read_json(input_json)
    records = data.get("records") or []
    included = [flatten(r) for r in records if r.get("included")]
    review = [flatten(r) for r in records if r.get("suggested_action") == "review"]
    excluded = [flatten(r) for r in records if r.get("suggested_action") == "exclude"]

    write_json(out / "final-claim.json", data)
    write_csv(out / "included-expenses.csv", included, FIELDS)
    write_csv(out / "review-required.csv", review, FIELDS)
    write_csv(out / "excluded-records.csv", excluded, FIELDS)
    copied = copy_sources(records, out)
    write_json(out / "attachment-copy-map.json", copied)

    lines = ["# Reimbursement Package", ""]
    lines.append(f"Included records: {len(included)}")
    lines.append(f"Review records: {len(review)}")
    lines.append(f"Excluded records: {len(excluded)}")
    lines.append("")
    lines.append("## Required User Review")
    lines.append("")
    if review:
        for r in review:
            lines.append(f"- {r.get('date','')} {r.get('merchant','')} {r.get('amount','')} {r.get('category','')} ({r.get('source_file','')})")
    else:
        lines.append("- No review items.")
    lines.append("")
    (out / "package-summary.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Build categorized reimbursement package.")
    parser.add_argument("--input", required=True, help="Classified/confirmed claim JSON.")
    parser.add_argument("--materials", help="Materials manifest JSON. Kept for CLI compatibility.")
    parser.add_argument("--out-dir", required=True, help="Output package directory.")
    args = parser.parse_args()
    build(args.input, args.materials, args.out_dir)


if __name__ == "__main__":
    main()

