# Complexity Report - Unit Tests

## Purpose
Verify ruff parsing logic for complexity violations.

---

## Test Scenarios

### CP-UT-001: Parse C901 Violation
**Description**: Extract function name and score.
**Input**: `path/to/file.py:10:1: C901 'my_func' is too complex (15 > 10)`
**Expected**: 
- Function: `my_func`
- Score: 15
- Module: detected from path

### CP-UT-002: Ignore Other Violations
**Description**: Ignore ruff errors that are not C901.
**Input**: `path.py:1: E501 line too long`
**Expected**: Ignored count.

### CP-UT-003: Module Aggregation
**Description**: Count violations per module.
**Input**: 3 violations in Module A, 1 in Module B.
**Expected**: Correct dictionary aggregation.

### CP-UT-004: Top Offenders Sorting
**Description**: Ensure top offenders list is sorted by score (descending).
**Input**: Function A (score 12), Function B (score 20).
**Expected**: B listed before A.
