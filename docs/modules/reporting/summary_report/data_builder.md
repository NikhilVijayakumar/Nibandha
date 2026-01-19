# Summary Report - Data Builder

## Overview
Aggregates JSON data from other reports.

---

## Logic

1. **Load Data**: Attempt to read:
   - `assets/data/unit_data.json`
   - `assets/data/e2e_data.json`
   - `assets/data/type_safety_data.json`
   - ... etc.

2. **Handle Missing**: If a report didn't run, fill with "N/A" or default values.

3. **Assess Health**:
   - IF any Critical Fail → **Status**: 🔴 FAIL
   - ELIF any Warning → **Status**: 🟡 NEEEDS ATTENTION
   - ELSE → **Status**: 🟢 PASSS

---

## Output Data Schema (`summary_data.json`)

```json
{
  "date": "2026-01-17",
  "overall_status": "🟡 NEEDS ATTENTION",
  
  "reports": {
    "unit": { "status": "🟢 PASS", "metrics": "43/43 passed" },
    "e2e": { "status": "🔴 FAIL", "metrics": "0/0 passed" },
    "type_safety": { "status": "🔴 FAIL", "metrics": "213 errors" },
    "complexity": { "status": "🟢 PASS", "metrics": "0 violations" }
  },

  "summary_table": "| Category | Status | ...",
  "links": {
    "unit": "data/unit_report.md",
    "e2e": "data/e2e_report.md"
  }
}
```
