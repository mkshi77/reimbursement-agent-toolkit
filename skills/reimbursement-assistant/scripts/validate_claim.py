import argparse
from datetime import datetime
from pathlib import Path

from lib_reimbursement import load_yaml_or_json, read_json, write_json


def parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def company_names(company):
    names = [company.get("company_name", "")]
    names.extend(company.get("aliases") or [])
    return {n.strip() for n in names if n}


def add_issue(issues, severity, record_id, message, source_file="", field=""):
    issues.append(
        {
            "severity": severity,
            "record_id": record_id,
            "field": field,
            "source_file": source_file,
            "message": message,
        }
    )


def validate(data, company=None, policy=None):
    company = company or {}
    policy = policy or {}
    claim = data.get("claim") or {}
    records = data.get("records") or []
    issues = []
    start = parse_date(claim.get("start_date"))
    end = parse_date(claim.get("end_date"))
    names = company_names(company)
    tax_id = str(company.get("tax_id") or "").strip()

    seen_invoices = {}
    for record in records:
        rid = record.get("id", "")
        source = record.get("source_file", "")
        action = record.get("suggested_action", "review")
        warnings = set(record.get("warnings") or [])

        if action == "review":
            add_issue(issues, "review", rid, record.get("reason") or "Record requires user confirmation.", source)
        if action == "exclude":
            continue
        if "vision_required" in warnings:
            add_issue(issues, "blocking", rid, "Visual file still needs OCR/vision extraction.", source)
        if record.get("amount") in ("", None):
            add_issue(issues, "blocking", rid, "Missing amount.", source, "amount")
        if not record.get("date") and record.get("category") not in {"approval_material"}:
            add_issue(issues, "review", rid, "Missing date.", source, "date")

        record_date = parse_date(record.get("date"))
        if start and end and record_date and not (start <= record_date <= end):
            add_issue(issues, "review", rid, "Record date is outside claim date range.", source, "date")

        buyer_name = str(record.get("buyer_name") or "").strip()
        buyer_tax_id = str(record.get("buyer_tax_id") or "").strip()
        if buyer_name and names and buyer_name not in names:
            add_issue(issues, "review", rid, f"Invoice buyer name does not match company profile: {buyer_name}", source, "buyer_name")
        if buyer_tax_id and tax_id and buyer_tax_id != tax_id:
            add_issue(issues, "review", rid, "Invoice buyer tax ID does not match company profile.", source, "buyer_tax_id")

        invoice_key = "|".join(
            [
                str(record.get("invoice_code") or "").strip(),
                str(record.get("invoice_number") or "").strip(),
            ]
        ).strip("|")
        if invoice_key:
            if invoice_key in seen_invoices:
                add_issue(issues, "blocking", rid, f"Duplicate invoice or ticket number also seen in {seen_invoices[invoice_key]}.", source, "invoice_number")
            else:
                seen_invoices[invoice_key] = rid

        if record.get("evidence_type") == "payment_record" and policy.get("review_rules", {}).get("require_review_for_payment_only", True):
            add_issue(issues, "review", rid, "Payment record should be matched to an invoice or receipt.", source)

    totals = {}
    for record in records:
        if record.get("included"):
            category = record.get("category") or "other"
            totals[category] = round(totals.get(category, 0) + float(record.get("amount") or 0), 2)

    return {"issues": issues, "totals": totals, "issue_count": len(issues)}


def render_markdown(validation):
    lines = ["# Reimbursement Validation Report", ""]
    lines.append(f"Issue count: {validation['issue_count']}")
    lines.append("")
    lines.append("## Totals")
    lines.append("")
    if validation["totals"]:
        for category, amount in sorted(validation["totals"].items()):
            lines.append(f"- {category}: {amount:.2f}")
    else:
        lines.append("- No included expenses.")
    lines.append("")
    lines.append("## Issues")
    lines.append("")
    if not validation["issues"]:
        lines.append("- No issues found.")
    else:
        for issue in validation["issues"]:
            source = f" ({issue['source_file']})" if issue.get("source_file") else ""
            record = f"[{issue['record_id']}]" if issue.get("record_id") else ""
            lines.append(f"- **{issue['severity']}** {record} {issue['message']}{source}")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Validate reimbursement records.")
    parser.add_argument("--input", required=True, help="Classified claim JSON.")
    parser.add_argument("--company", help="Company profile YAML or JSON.")
    parser.add_argument("--policy", help="Policy YAML or JSON.")
    parser.add_argument("--output", required=True, help="Output .md or .json report.")
    args = parser.parse_args()

    data = read_json(args.input)
    company = load_yaml_or_json(args.company) if args.company else {}
    policy = load_yaml_or_json(args.policy) if args.policy else {}
    validation = validate(data, company, policy)

    if Path(args.output).suffix.lower() == ".json":
        write_json(args.output, validation)
    else:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(render_markdown(validation))


if __name__ == "__main__":
    main()
