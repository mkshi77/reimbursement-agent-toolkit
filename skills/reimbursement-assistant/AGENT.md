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

When the user provides files directly in a chat or messaging app, first show a chat intake checklist and ask before saving to the default working folder unless the user already provided a target folder.

When the user provides only materials and a company form, create draft company/profile/policy questions instead of stopping.

If a company profile, policy, and template map already exist from a previous run, reuse them by default. Ask again only when the user says the company form, invoice header, tax ID, reimbursement rules, or approval rules changed.

## Chat-First Intake Gate

Always begin with a startup checklist in the conversation before running the full command sequence. The first response must not be a file link and must not come after OCR, classification, validation, filling, or packaging. The checklist must show:

- materials: present, missing, or saved from chat attachments
- company Excel form: provided, reused from prior configuration, or missing
- company profile: present, missing, or draft-needed
- reimbursement policy: present, missing, or draft-needed
- output location: user-provided folder or default run folder

Default run folder:

```text
reimbursement-runs/YYYYMMDD-HHMMSS/
  raw/
  materials/
  extracted/
  review/
  output/
  session.json
```

If attachments arrive through chat, propose copying them into `raw/` and `materials/`, then wait for the user to say to start or change the path. If the user supplied a folder path, either use it as the material source or copy it into the run folder with `scripts/prepare_run.py` after the intake step.

If materials are missing, stop after the checklist and ask the user to upload files or provide a folder. If the company Excel form is missing and no previous template map exists, offer two choices: upload the company form, or continue with material organization only and fill the form later.

Use this staged default:

1. Intake only: show checklist and wait.
2. Save and scan only: create the run folder, copy files, scan file counts, then report in chat.
3. Extract and classify: run OCR/vision/extraction only after user approval.
4. Confirm in chat: paste the checkbox checklist into the conversation and wait.
5. Finalize: validate, fill Excel, and package only after confirmation.

## Required Behavior

1. Do the chat intake gate first; run the full pipeline only after minimum inputs are present and the user approves the next step.
2. Ask the user only for missing materials, missing company form choices, missing company rules, ambiguous company form fields, and questionable expenses.
3. Show every extracted expense item in the chat before finalizing the claim.
4. Do not silently include low-confidence or abnormal records.
5. Preserve source file references for every extracted item.
6. Keep company-specific information in config files, not in code.
7. Do not fill the final Excel workbook until the user confirms the checklist or explicitly accepts the suggested selections.
8. Do not require the user to open generated Markdown, CSV, or Excel files for confirmation; generated files are backup/output only.

## Command Sequence

```bash
python scripts/prepare_run.py --input MATERIALS_DIR --out-root reimbursement-runs
python scripts/scan_materials.py --input RUN_DIR/materials --output RUN_DIR/extracted/materials.json
python scripts/extract_receipts.py --materials RUN_DIR/extracted/materials.json --output RUN_DIR/extracted/extracted.json
python scripts/classify_expenses.py --input RUN_DIR/extracted/extracted.json --output RUN_DIR/review/classified.json
python scripts/validate_claim.py --input RUN_DIR/review/classified.json --company company-profile.yaml --policy travel-policy.yaml --output RUN_DIR/review/issues.md
python scripts/build_package.py --input RUN_DIR/review/classified.json --materials RUN_DIR/extracted/materials.json --out-dir RUN_DIR/output/package
python scripts/fill_template.py --input RUN_DIR/review/classified.json --template template.xlsx --map template-map.json --output RUN_DIR/output/reimbursement.xlsx
```

If images or PDFs need OCR, use the agent's visual model or an external OCR tool, then pass the extracted records to `extract_receipts.py --agent-records records.json`.

## Confirmation UX

Display records in the chat as a checkbox checklist grouped by suggested action:

- include
- review
- exclude

Each row must show:

`[checkbox] record_id | date | merchant | amount | category | invoice_id | source_file | confidence | reason`

Example:

```markdown
## 待确认费用

- [x] R001 | 2026-06-10 | 滴滴出行 | 38.50 元 | 市内交通 | 来源：wechat_01.png | 置信度：0.92
- [ ] R002 | 2026-06-10 | 微信转账 | 200.00 元 | 疑似私人支出 | 来源：wechat_02.png | 建议排除
- [ ] R003 | 2026-06-11 | 酒店 | 420.00 元 | 住宿费 | 来源：hotel.pdf | 税号需确认
```

Only ask the user about rows marked `review`, rows with warnings, missing company rules, ambiguous company form fields, and any included row the user wants to edit.

Accept concise user replies such as "确认 R001，排除 R002，R003 改成住宿费并纳入".

If there are many records, show them in chat batches of about 8-12 items and ask the user whether to continue, filter, or accept all suggested inclusions. Never make a file the only confirmation surface.
