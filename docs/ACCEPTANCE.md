# Acceptance Gate

This document records the release gate used for the first toolkit version.

## 1. Skill Usability

Passed when:

- The Codex `SKILL.md` validates with `quick_validate.py`.
- The command-line workflow runs end to end on sample materials.
- Scripts produce machine-readable JSON and user-readable reports.
- Excel filling works with a mapped template.
- Package generation creates review, included, excluded, and summary outputs.

Validation command:

```bash
python scripts/scan_materials.py --input MATERIALS_DIR --output work/materials.json
python scripts/extract_receipts.py --materials work/materials.json --output work/extracted.json
python scripts/classify_expenses.py --input work/extracted.json --output work/classified.json
python scripts/validate_claim.py --input work/classified.json --company company-profile.yaml --policy travel-policy.yaml --output work/issues.md
python scripts/fill_template.py --input work/classified.json --template template.xlsx --map template-map.json --output work/reimbursement.xlsx
python scripts/build_package.py --input work/classified.json --materials work/materials.json --out-dir work/package
```

## 2. Don't Make Me Think

Passed when:

- The agent performs scanning, extraction, classification, validation, and packaging before asking broad questions.
- Every extracted line item is available for user review.
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
- Codex skill validation passes.

