# Type Safety Report - Data Builder

## Overview
The `TypeSafetyDataBuilder` is responsible for parsing raw `mypy` output line-by-line to extract structured error data.

---

## Parsing Logic

### Input Format (mypy)
Standard mypy output lines look like:
```text
src/nikhil/pravaha/domain/storage/logic/version_resolver.py:19: error: Returning Any from function declared to return "Path"  [no-any-return]
src/nikhil/pravaha/domain/auth/protocol.py:8: error: Skipping analyzing "data": module is installed, but missing stubs  [import-untyped]
```

### Parsing Regex
We use a regex to capture: `path`, `line`, `severity` (error/note), `message`, and `error_code`.
```python
pattern = re.compile(r"^([^:]+):(\d+):\s+(\w+):\s+(.*)\s+\[(.*)\]$")
```

### Module Detection
For each error, we determine the **Module** it belongs to based on the file path.
- **Logic**: Inspect path components after `src/nikhil/nibandha/`. 
- **Example**: `src/nikhil/nibandha/reporting/core.py` → **Reporting**
- **Fallback**: If not in standard structure, use the top-level folder name or "Root".

---

## Output Data Schema (`type_safety_data.json`)

```json
{
  "date": "2026-01-17",
  "tool": "mypy --strict",
  "status": "🔴 FAIL",
  "total_errors": 213,
  "unique_modules_affected": 8,
  
  "metrics": {
    "total": 213,
    "by_severity": {
      "error": 213,
      "note": 0
    }
  },

  "errors_by_module": {
    "Storage": 73,
    "Workflow": 50,
    "Auth": 26,
    "Bot": 22,
    "Api": 21,
    "Llm": 14,
    "Config": 0,
    "Pravaha_logging": 0
  },

  "errors_by_category": {
    "import-untyped": 45,
    "no-any-return": 30,
    "misc": 20
  },

  "module_table": "| Module | Status | Errors |\n|:---|:---:|:---:|\n| **Storage** | 🔴 FAIL | 73 |...",
  
  "critical_errors_block": "src/.../file.py:19: error: ... [no-any-return]\n..."
}
```

## Transformations

1. **Status Determination**:
   - 0 errors: 🟢 PASS
   - >0 errors: 🔴 FAIL

2. **Parsing**:
   - Convert absolute paths to project-relative paths for readability.
   - Aggregate counts by module.
   - Aggregate counts by error code (category).

3. **Formatting**:
   - `module_table`: Pre-rendered markdown table sorted by error count (descending).
   - `critical_errors_block`: Raw text block of errors for the `<details>` section, filtered if necessary (e.g., show top 50 if too many).
