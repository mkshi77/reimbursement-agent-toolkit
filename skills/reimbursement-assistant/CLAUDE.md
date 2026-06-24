# Claude Code Entry

Use the same workflow as `AGENT.md`.

When using Claude Code:

1. Read `SKILL.md` for the reimbursement workflow.
2. Start with the chat intake checklist from `SKILL.md`; do not run OCR, extraction, classification, validation, filling, or packaging before the first chat response.
3. Wait for the user to approve the next step or change the output folder.
4. Use `scripts/prepare_run.py` or an equivalent copy step to save chat attachments and source folders into a timestamped run folder after approval.
5. Use `scripts/` for deterministic file operations.
6. Use Claude's image/PDF reasoning to extract records from screenshots when local OCR is unavailable.
7. Save extracted records as JSON matching `schemas/claim.schema.json`.
8. Present the checkbox review checklist directly in chat before filling the final workbook.
9. Run validation scripts before presenting the final package.

Do not finalize a reimbursement form until the user has confirmed the per-item review table or explicitly accepted the suggested selections.

Prefer natural user prompts over command-style prompts. If the user says "I uploaded the reimbursement files and company form, start organizing", infer the visible materials and company Excel form from the available files, then show the intake checklist and ask before long processing.

If the user sends receipts and forms directly in chat, ask before saving to the default working folder, then save attachments before running scripts. If prior company configuration exists, reuse it unless the user says the company form or reimbursement rules changed.
