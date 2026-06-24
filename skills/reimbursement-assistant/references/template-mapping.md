# Template Mapping

Template maps decouple company Excel layouts from reimbursement logic.

## Field Mapping

Use dotted paths for claim fields:

```json
{
  "claim.applicant": "B3",
  "claim.department": "D3"
}
```

## Expense Table Mapping

Use column letters and a start row:

```json
{
  "expense_table": {
    "start_row": 10,
    "max_rows": 20,
    "columns": {
      "date": "A",
      "merchant": "B",
      "category": "C",
      "amount": "E"
    }
  }
}
```

If a new template changes cell locations, regenerate only the map. Do not change scripts unless the table structure cannot be represented.

