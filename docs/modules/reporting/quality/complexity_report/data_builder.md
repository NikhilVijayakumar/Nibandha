# Complexity Report - Data Builder

## Overview
The `ComplexityDataBuilder` parses `ruff` output to identify complexity violations (specifically rule `C901`).

---

## Parsing Logic

### Input Format (ruff)
```text
src/nikhil/pravaha/domain/workflow/logic.py:45:5: C901 'process_graph' is too complex (15 > 10)
src/nikhil/pravaha/api/routes.py:12:1: C901 'handle_request' is too complex (12 > 10)
```

### Parsing Regex
Pattern matches:
- File path
- Line number
- Violation code (`C901`)
- Message (containing function name and complexity score)

### Extraction
- **Function Name**: Extracted from message `'process_graph'`
- **Score**: Extracted specifically from `(15 > 10)` part.
- **Module**: Same path-to-module logic as Type Safety.

---

## Output Data Schema (`complexity_data.json`)

```json
{
  "date": "2026-01-17",
  "tool": "ruff",
  "status": "🟢 PASS",
  "total_violations": 0,
  
  "violations_by_module": {
    "Workflow": 1,
    "Api": 1
  },
  
  "top_complex_functions": [
    {
      "module": "Workflow",
      "function": "process_graph",
      "score": 15,
      "location": "src/.../logic.py:45"
    }
  ],

  "module_breakdown": "| Module | Violations | Max Score |\n...",
  "detailed_violations_block": "src/...: C901 ..."
}
```
