# Universal Agent Instructions

This toolkit is agent-agnostic. Any agent that can read files and run Python can use it.

## Primary Goal

Prepare a reimbursement package from loose materials while minimizing user decisions.

## Natural User Requests

Users should not need to know script names or JSON file names. Treat requests like these as sufficient:

- "I uploaded my reimbursement materials and company Excel template. Start organizing them."
- "The reimbursement files are in `materials/`; the company template is `template.xlsx`. Please identify every expense and show me the confirmation table first."
- "Help me organize this travel reimbursement folder. If company rules are missing, ask me only for the missing rules."
- "I sent the receipts, screenshots, and company reimbursement form in this chat. Start organizing them."
- "Use last time's company reimbursement form. I uploaded new materials."

When the user provides files directly in a chat or messaging app, save the attachments into a working materials folder first, then run the same workflow.

When the user provides only materials and a company form, create draft company/profile/policy questions instead of stopping.

If a company profile, policy, and template map already exist from a previous run, reuse them by default. Ask again only when the user says the company form, invoice header, tax ID, reimbursement rules, or approval rules changed.

## Required Behavior

1. Do the mechanical work first: scan, extract, classify, validate, and draft outputs.
2. Ask the user only for missing company rules, ambiguous company form fields, and questionable expenses.
3. Show every extracted expense item before finalizing the claim.
4. Do not silently include low-confidence or abnormal records.
5. Preserve source file references for every extracted item.
6. Keep company-specific information in config files, not in code.

## Command Sequence

```bash
python scripts/scan_materials.py --input MATERIALS_DIR --output work/materials.json
python scripts/extract_receipts.py --materials work/materials.json --output work/extracted.json
python scripts/classify_expenses.py --input work/extracted.json --output work/classified.json
python scripts/validate_claim.py --input work/classified.json --company company-profile.yaml --policy travel-policy.yaml --output work/issues.md
python scripts/fill_template.py --input work/classified.json --template template.xlsx --map template-map.json --output work/reimbursement.xlsx
python scripts/build_package.py --input work/classified.json --materials work/materials.json --out-dir work/package
```

If images or PDFs need OCR, use the agent's visual model or an external OCR tool, then pass the extracted records to `extract_receipts.py --agent-records records.json`.

## Confirmation UX

Display records grouped by suggested action:

- include
- review
- exclude

Each row must show:

`include | date | merchant | amount | category | invoice_id | source_file | confidence | reason`

Only ask the user about rows marked `review`, rows with warnings, missing company rules, ambiguous company form fields, and any included row the user wants to edit.
