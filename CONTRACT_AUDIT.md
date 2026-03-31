# CONTRACT AUDIT (Flutter -> Backend)

This repository includes a deterministic machine-readable artifact: `contract_report.json`.

## What it contains
- Endpoint signatures (method/path/auth/request/response)
- Serializer and router source mappings
- Field-level mappings for Flutter `fromJson` models
- Enum translation tables
- Validation summary and residual risks

## Regeneration

```bash
npm run contract:generate
```

## CI Drift Check

```bash
npm run contract:check
```

`contract:check` regenerates into a temp file and fails if `contract_report.json` has drifted.
