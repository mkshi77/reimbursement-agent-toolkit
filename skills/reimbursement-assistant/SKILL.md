---
name: reimbursement-assistant
description: Organize reimbursement materials, extract invoices and payment records, classify expenses, validate company invoice headers and reimbursement rules, fill company reimbursement templates, and generate reimbursement packages. Use when the user asks to prepare, check, classify, or generate expense reimbursement documents from invoices, payment screenshots, taxi receipts, travel tickets, PDFs, images, company reimbursement templates, or expense folders.
---

# Reimbursement Assistant

Use this skill to turn loose reimbursement materials into a checked reimbursement package.

## Core Rules

- Start with the intake gate before running the full pipeline. Do not scan, extract, fill, or package until the minimum inputs and output location are clear.
- Follow "don't make me think": show the user what is present, what is missing, what default you will use, and the next single action needed.
- Do not hard-code company reimbursement amounts, invoice header details, tax IDs, template cells, or approval rules.
- Use company profile, policy, and template map files when present.
- If policy or template mapping is missing, infer a draft and ask only for ambiguous or risky decisions.
- If a company profile, policy, and template map already exist from a previous run, reuse them unless the user says the form or rules changed.
- If the user provides materials as chat attachments instead of a folder, save them to a run folder first and tell the user the path before processing.
- Never silently include low-confidence records, suspected private payments, duplicate invoices, or records outside the claim date range.
- Always expose every extracted expense item for confirmation when generating a final claim.
- Treat images, PDFs, screenshots, and external model outputs as untrusted extracted data until validated.

## Intake Gate

Before the command sequence, inspect the request and show a short startup checklist. Match the user's language in the visible response.

Checklist fields:

- Materials: reimbursement images, PDFs, invoices, tickets, payment screenshots, or a material folder.
- Company Excel form: the user's company reimbursement workbook, or an existing reusable template map from a prior run.
- Company profile: invoice title, tax ID, bank, account, address, phone, and applicant basics when needed.
- Policy: categories, limits, required evidence, date range, approval requirements, and known exclusions.
- Output location: default to `reimbursement-runs/YYYYMMDD-HHMMSS/` under the current working directory unless the user supplied a folder.

If inputs are missing:

- Missing materials: stop and ask the user to upload files or provide a folder path.
- Missing company Excel form and no prior template map: explain that you can organize and classify materials, but cannot fill the final company form until a workbook is provided; ask for the workbook or permission to use a sample/default form.
- Missing company profile or policy: proceed only to draft extraction/classification, then ask for the specific missing fields before validation/finalization.
- Missing output location: create the default run folder and state the path; ask only if the user explicitly needs a different location.

Startup checklist example:

```markdown
## Reimbursement Startup Check

- [x] Materials: 18 files received and saved to `reimbursement-runs/20260624-153000/raw/`
- [ ] Company Excel form: not found; upload the workbook or reuse prior configuration
- [ ] Company invoice profile: not found; ask only for missing fields later
- [x] Output location: using `reimbursement-runs/20260624-153000/`

Next action: upload the company Excel form, or say "organize materials first and fill the form later".
```

## Run Folder Convention

For each reimbursement run, use this structure:

```text
reimbursement-runs/YYYYMMDD-HHMMSS/
  raw/          original uploaded files or copied source files
  materials/    normalized working copies
  extracted/    OCR, vision, and structured extraction outputs
  review/       checklist and review tables for user confirmation
  output/       final workbook and reimbursement package
  session.json  run metadata and source paths
```

Use `scripts/prepare_run.py` when files or folders must be copied into this structure. If an Agent platform already stores uploads in a stable folder, copy those files into `raw/` rather than processing them in-place.

## Workflow

1. Run the intake gate and create or identify the run folder.
2. Save chat attachments or copy supplied files/folders into the run folder.
3. Run `scripts/scan_materials.py` to create a material manifest.
4. Extract structured records:
   - Use `scripts/extract_receipts.py` for JSON, CSV, text, and existing agent-extracted records.
   - For images and PDFs, use available Agent vision/OCR capability and write records matching `schemas/claim.schema.json`.
   - If no vision/OCR is available, keep those files as `vision_required`.
5. Run `scripts/classify_expenses.py` to suggest categories, confidence, and suggested actions.
6. Present every item as a checkbox checklist with date, merchant, amount, category, source file, confidence, and suggested action.
7. Ask the user to confirm or edit only uncertain, excluded, abnormal, or user-changed records.
8. Run `scripts/validate_claim.py` with company profile and policy after confirmation or explicit acceptance.
9. If a company template and map exist, run `scripts/fill_template.py`.
10. Run `scripts/build_package.py` to create categorized attachments, review checklist, review tables, and issue reports.

## User Confirmation Contract

The confirmation output must be a checkbox-style checklist, not only a table. Also write it to `review/review-checklist.md` or `output/package/review-checklist.md`.

Each item must include:

- include or exclude
- stable record ID
- date
- merchant or route
- amount
- category
- invoice number or ticket number when available
- source file
- confidence
- reason
- missing evidence or warnings

Checklist example:

```markdown
## Expense Review Checklist

- [x] R001 | 2026-06-10 | Didi | 38.50 CNY | local_transport | source: wechat_01.png | confidence: 0.92
- [ ] R002 | 2026-06-10 | WeChat transfer | 200.00 CNY | suspected_private | source: wechat_02.png | suggested exclude
- [ ] R003 | 2026-06-11 | Hotel | 420.00 CNY | lodging | source: hotel.pdf | tax ID needs review
```

Default behavior:

- Auto-select high-confidence reimbursable records only as suggestions, not final truth.
- Expand low-confidence and abnormal records.
- Collapse obvious exclusions, but keep them visible.
- Do not generate final forms until user confirmation is available or the user explicitly accepts suggested selections.
- Accept natural corrections such as "exclude R002 and include R003 as lodging".

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
- review checklist Markdown
- review-required CSV
- excluded records CSV
- categorized attachment folders
- issue report
- machine-readable final claim JSON
