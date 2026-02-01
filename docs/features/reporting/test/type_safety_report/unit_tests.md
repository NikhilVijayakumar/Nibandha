# Type Safety Report - Unit Tests

## Purpose
Verify the parsing logic, module attribution, and data structuring of the `TypeSafetyDataBuilder`.

---

## Test Scenarios

### TS-UT-001: Parse Valid Mypy Output
**Description**: Correctly parses standard mypy error lines.
**Input**: Raw string with file path, line, error message, code.
**Expected**: 
- Extraction of file path, line number, message, error code.
- Correct count aggregation.

### TS-UT-002: Module Detection (Standard Structure)
**Description**: Correctly identifies module from `src/nikhil/nibandha/MODULE/file.py`.
**Input**: Path `src/nikhil/nibandha/reporting/core.py`.
**Expected**: Module detected as "Reporting".

### TS-UT-003: Module Detection (Fallback)
**Description**: Handles paths outside standard structure gracefully.
**Input**: Path `scripts/run_analysis.py`.
**Expected**: Module detected as "Scripts" or similar logical name.

### TS-UT-004: Empty Mypy Output
**Description**: Handles case where mypy finds no errors (success).
**Input**: Empty string / "Success: ...".
**Expected**: 
- `total_errors` = 0
- `status` = 🟢 PASS
- `module_table` indicates generic pass or is empty.

### TS-UT-005: Parse Error Codes
**Description**: Correctly aggregates errors by category.
**Input**: Mixed errors (`[arg-type]`, `[return-value]`).
**Expected**: `errors_by_category` contains correct counts for each.

### TS-UT-006: Windows Path Handling
**Description**: Handles Windows backslashes in parsing logic.
**Input**: `src\nikhil\nibandha\core\utils.py`.
**Expected**: Module "Core" detected correctly despite separators.

### TS-UT-007: Table Sorting
**Description**: `module_table` is sorted by error count (descending).
**Input**: Module A (5 errors), Module B (10 errors).
**Expected**: Table lists Module B first.

---

## Implementation

**File**: `tests/unit/reporting/type_safety/test_type_safety_builder.py`

```python
def test_parse_valid_mypy_output(builder):
    output = "src/file.py:10: error: bad type [arg-type]"
    data = builder.build_type_safety(output)
    assert data["total_errors"] == 1
    assert data["errors_by_category"]["arg-type"] == 1

def test_module_detection_logic(builder):
    path = "src/nikhil/nibandha/auth/login.py"
    module = builder._extract_module(path)
    assert module == "Auth"
```
