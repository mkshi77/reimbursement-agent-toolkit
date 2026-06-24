# Acceptance Gate

This document records the release gate used for the first toolkit version.

## 1. Skill Usability

Passed when:

- The Codex `SKILL.md` validates with `quick_validate.py`.
- The skill starts with a chat intake checklist before any long-running OCR, extraction, classification, validation, filling, or packaging.
- The agent waits for user confirmation before saving to a default folder or starting long processing, unless the user explicitly requested full-auto mode.
- Chat attachments or supplied folders can be copied into a timestamped run folder.
- The command-line workflow runs end to end on sample materials.
- Scripts produce machine-readable JSON and user-readable reports.
- Excel filling works with a mapped template.
- Package generation creates a checkbox review checklist, review CSV, included CSV, excluded CSV, and summary outputs.

Validation command:

```bash
python scripts/prepare_run.py --input MATERIALS_DIR --out-root reimbursement-runs
python scripts/scan_materials.py --input RUN_DIR/materials --output RUN_DIR/extracted/materials.json
python scripts/extract_receipts.py --materials RUN_DIR/extracted/materials.json --output RUN_DIR/extracted/extracted.json
python scripts/classify_expenses.py --input RUN_DIR/extracted/extracted.json --output RUN_DIR/review/classified.json
python scripts/validate_claim.py --input RUN_DIR/review/classified.json --company company-profile.yaml --policy travel-policy.yaml --output RUN_DIR/review/issues.md
python scripts/build_package.py --input RUN_DIR/review/classified.json --materials RUN_DIR/extracted/materials.json --out-dir RUN_DIR/output/package
python scripts/fill_template.py --input RUN_DIR/review/classified.json --template template.xlsx --map template-map.json --output RUN_DIR/output/reimbursement.xlsx
```

## 2. Don't Make Me Think

Passed when:

- The agent first shows a short startup checklist with materials, company form, company profile, policy, and output location status.
- The first response is in the chat, not a generated Markdown/CSV file.
- Missing inputs are explained with a specific next action; the user is not expected to infer what to upload.
- Uploaded files are saved or copied into a visible run folder only after the user accepts the default path or supplies another path.
- Every extracted line item is available for user review directly in the chat.
- The primary user review surface is a chat checkbox-style checklist with stable record IDs; generated files are backup/output only.
- Low-confidence, payment-only, tax mismatch, duplicate, and visual-only records are not silently included.
- Obvious exclusions remain visible but do not block unrelated reimbursable records.

## 3. Multi-Agent Compatibility

Passed when:

- Core behavior lives in scripts, schemas, and references.
- Codex, Claude Code, and generic agents have separate entry instructions.
- Image/PDF recognition is an replaceable extraction step through `--agent-records`.
- Company policy and template layout are external configuration files.

## Current Smoke-Test Result

The sample workflow passes:

- 4 records extracted.
- Local transport, intercity transport, lodging, and non-reimbursable transfer are classified.
- Payment-only and tax-header mismatch issues are reported.
- `review-checklist.md` is generated for checkbox-style confirmation.
- Codex skill validation passes.
