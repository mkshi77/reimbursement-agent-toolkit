# Claude Code Entry

Use the same workflow as `AGENT.md`.

When using Claude Code:

1. Read `SKILL.md` for the reimbursement workflow.
2. Start with the intake checklist from `SKILL.md`; do not immediately run the full pipeline when materials, company form, or output location are unclear.
3. Use `scripts/prepare_run.py` or an equivalent copy step to save chat attachments and source folders into a timestamped run folder.
4. Use `scripts/` for deterministic file operations.
5. Use Claude's image/PDF reasoning to extract records from screenshots when local OCR is unavailable.
6. Save extracted records as JSON matching `schemas/claim.schema.json`.
7. Present the checkbox review checklist before filling the final workbook.
8. Run validation scripts before presenting the final package.

Do not finalize a reimbursement form until the user has confirmed the per-item review table or explicitly accepted the suggested selections.

Prefer natural user prompts over command-style prompts. If the user says "I uploaded the reimbursement files and company form, start organizing", infer the materials and company Excel form from the available files, then ask only for missing company rules or ambiguous form fields.

If the user sends receipts and forms directly in chat, save the attachments into a working folder before running scripts. If prior company configuration exists, reuse it unless the user says the company form or reimbursement rules changed.
