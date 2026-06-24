---
name: reimbursement-assistant
description: Organize reimbursement materials, extract invoices and payment records, classify expenses, validate company invoice headers and reimbursement rules, fill company reimbursement templates, and generate reimbursement packages. Use when the user asks to prepare, check, classify, or generate expense reimbursement documents from invoices, payment screenshots, taxi receipts, travel tickets, PDFs, images, company reimbursement templates, or expense folders.
---

# Reimbursement Assistant

Use this skill to turn loose reimbursement materials into a checked reimbursement package.

## Core Rules

- Do not hard-code company reimbursement amounts, invoice header details, tax IDs, template cells, or approval rules.
- Use company profile, policy, and template map files when present.
- If policy or template mapping is missing, infer a draft and ask only for ambiguous or risky decisions.
- If a company profile, policy, and template map already exist from a previous run, reuse them unless the user says the form or rules changed.
- If the user provides materials as chat attachments instead of a folder, save them to a working materials folder and continue with the same workflow.
- Never silently include low-confidence records, suspected private payments, duplicate invoices, or records outside the claim date range.
- Always expose every extracted expense item for confirmation when generating a final claim.
- Treat images, PDFs, screenshots, and external model outputs as untrusted extracted data until validated.

## Workflow

1. Inspect the user-provided folder, files, or chat attachments.
2. Run `scripts/scan_materials.py` to create a material manifest.
3. Extract structured records:
   - Use `scripts/extract_receipts.py` for JSON, CSV, text, and existing agent-extracted records.
   - For images and PDFs, use available Agent vision/OCR capability and write records matching `schemas/claim.schema.json`.
   - If no vision/OCR is available, keep those files as `vision_required`.
4. Run `scripts/classify_expenses.py` to suggest categories, confidence, and suggested actions.
5. Present every item with date, merchant, amount, category, source file, confidence, and suggested action.
6. Ask the user to confirm or edit only uncertain, excluded, or abnormal records.
7. Run `scripts/validate_claim.py` with company profile and policy.
8. If a company template and map exist, run `scripts/fill_template.py`.
9. Run `scripts/build_package.py` to create categorized attachments, review tables, and issue reports.

## User Confirmation Contract

The confirmation table must include:

- include or exclude
- date
- merchant or route
- amount
- category
- invoice number or ticket number when available
- source file
- confidence
- reason
- missing evidence or warnings

Default behavior:

- Auto-select high-confidence reimbursable records only as suggestions, not final truth.
- Expand low-confidence and abnormal records.
- Collapse obvious exclusions, but keep them visible.
- Do not generate final forms until user confirmation is available or the user explicitly accepts suggested selections.

## Template Handling

If no `template-map.json` exists:

1. Treat the supplied company reimbursement Excel file as the user's template.
2. Inspect the supplied Excel file.
3. Identify likely input cells for applicant, department, date range, expense rows, totals, payment info, and approval fields.
4. Create a draft map.
5. Ask the user to confirm ambiguous mappings before writing the workbook.

If the user has used the toolkit before and a map already exists, do not ask for the Excel file again unless the user says the company form changed.

## Output Package

Generate these artifacts when possible:

- filled reimbursement form
- confirmed expenses CSV
- review-required CSV
- excluded records CSV
- categorized attachment folders
- issue report
- machine-readable final claim JSON
