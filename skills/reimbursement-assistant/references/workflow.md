# Workflow Reference

## Setup Mode

Use setup mode when the user has not configured their company:

1. Collect company invoice header and tax ID.
2. Collect reimbursement policies or ask the user to upload policy documents.
3. Ask the user to upload the company reimbursement Excel template.
4. Create or update `company-profile.yaml`, `travel-policy.yaml`, and `template-map.json`.
5. Do not guess subsidy amounts or approval thresholds without user confirmation.

## Daily Mode

Use daily mode when the user provides a material folder:

1. Scan files.
2. Extract records.
3. Classify records.
4. Build the per-item confirmation table.
5. Validate against company profile and policy.
6. Fill template.
7. Build package.

## Finalization Gate

Before generating final forms, ensure one of these is true:

- The user confirmed the per-item table.
- The user explicitly accepted all suggested selections.

