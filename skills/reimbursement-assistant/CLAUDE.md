# Claude Code Entry

Use the same workflow as `AGENT.md`.

When using Claude Code:

1. Read `SKILL.md` for the reimbursement workflow.
2. Use `scripts/` for deterministic file operations.
3. Use Claude's image/PDF reasoning to extract records from screenshots when local OCR is unavailable.
4. Save extracted records as JSON matching `schemas/claim.schema.json`.
5. Run validation scripts before presenting the final package.

Do not finalize a reimbursement form until the user has confirmed the per-item review table or explicitly accepted the suggested selections.

