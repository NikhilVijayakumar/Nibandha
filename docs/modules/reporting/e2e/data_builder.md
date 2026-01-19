# E2E Test Report - Data Builder

## Overview
Parses test results specifically marked as E2E or system tests.

---

## Logic

### Input
- Similar to Unit Report (`pytest --json-report`).
- Filter: Select tests marked `@e2e` or in `tests/e2e/`.

### Extra Metrics
- **Duration**: E2E tests are time-sensitive. Track `duration` per scenario.
- **Screenshots**: If tests save screenshots on failure, link them here.

---

## Output Data Schema (`e2e_data.json`)

```json
{
  "date": "2026-01-17",
  "status": "🔴 FAIL",
  
  "summary": {
    "total_scenarios": 15,
    "passed": 14,
    "failed": 1,
    "duration_total": 45.2
  },

  "slowest_scenarios": [
    {"name": "test_checkout_flow", "duration": 12.5},
    {"name": "test_login", "duration": 5.2}
  ],

  "failures": [
    {
      "name": "test_payment_gateway",
      "error": "TimeoutError",
      "screenshot": "assets/screens/fail_123.png"
    }
  ],

  "detailed_table": "| Scenario | Status | Duration | ..."
}
```
