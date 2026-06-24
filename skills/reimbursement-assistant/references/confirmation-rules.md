# Confirmation Rules

## Always Show These Columns

- include
- date
- merchant or route
- amount
- category
- evidence type
- source file
- invoice number
- confidence
- suggested action
- reason
- warnings

## Suggested Action Rules

- `include`: likely reimbursable, high confidence, date and evidence look valid.
- `review`: unclear purpose, low confidence, missing invoice, payment-only, tax mismatch, date mismatch, duplicate risk.
- `exclude`: likely income, transfer, private spending, duplicate, refund, or unrelated record.

## User Experience

- Show summaries first.
- Then show every line item.
- Expand `review` rows by default.
- Keep `exclude` rows visible but collapsed where the UI supports it.
- Never hide source file references.

