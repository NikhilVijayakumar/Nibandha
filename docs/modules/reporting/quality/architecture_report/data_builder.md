# Architecture Report - Data Builder

## Overview
Parses output from `lint-imports` to track contract violations.

---

## Parsing Logic

### Input Format (import-linter)
```text
Broken contracts:
1. Domain layer must not import Infrastructure
    kept: False
    violations:
        src.domain.x imports src.infra.y
```

### Logic
1. Identify **Contracts**: Name of rule being checked.
2. Identify **Status**: Kept (Pass) vs Broken (Fail).
3. Extract **Violations**: Specific import paths causing the break.

---

## Output Data Schema

```json
{
  "date": "2026-01-17",
  "tool": "import-linter",
  "status": "🔴 FAIL",
  "configured": true,
  
  "contracts": [
    {
      "name": "Domain isolated from Infrastructure",
      "status": "kept"
    },
    {
      "name": "API isolated from Database",
      "status": "broken",
      "violations": [
        "src.api.routes -> src.db.models"
      ]
    }
  ],
  
  "layer_summary_table": "| Contract | Status |\n...",
  "detailed_violations": "..."
}
```

**Special Case**: If no configuration found, status is `⚠️ NOT CONFIGURED`.
