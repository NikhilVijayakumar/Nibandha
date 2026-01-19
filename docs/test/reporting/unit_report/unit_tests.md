# Unit Report - Unit Tests

## Purpose

Unit-level tests specific to **Unit Report** functionality. These tests verify the unique data extraction, calculations, and formatting logic for unit test reports.

---

## Scope

Tests the following **specific to unit reports**:
- Pytest JSON parsing for unit tests
- Pass rate calculations
- Coverage metric extraction
- Module breakdown table generation
- Failure details extraction

**Note**: General template/viz/builder tests are in [`common/`](../common/)

---

## Test Scenarios

### UR-UT-001: Pytest JSON Extraction

**Description**: Extract summary from pytest JSON correctly

**Input**:
- Valid pytest JSON with summary section

**Expected**:
- Total tests extracted
- Passed/failed/skipped counts correct
- Matches pytest JSON exactly

**Priority**: P0

---

### UR-UT-002: Pass Rate Calculation

**Description**: Calculate pass rate percentage accurately

**Input**:
- Passed: 148, Total: 150

**Expected**:
- Pass rate = 98.7%
- Rounded to 1 decimal

**Priority**: P0

---

### UR-UT-003: Coverage Extraction

**Description**: Extract overall coverage percentage

**Input**:
- Coverage JSON with totals.percent_covered

**Expected**:
- Extract correct percentage
- Round appropriately

**Priority**: P0

---

### UR-UT-004: Module Coverage Breakdown

**Description**: Extract per-module coverage metrics

**Input**:
- Coverage JSON with files section

**Expected**:
- Map file paths to module names
- Extract coverage % per module
- Handle missing modules

**Priority**: P1

---

### UR-UT-005: Module Breakdown Table

**Description**: Generate module breakdown markdown table

**Input**:
- Module test results

**Expected**:
- Valid markdown table
- Columns: Module, Tests, Passed, Failed
- Sorted by module name

**Priority**: P1

---

### UR-UT-006: Failure Details Extraction

**Description**: Extract detailed failure information

**Input**:
- Pytest JSON with failed tests

**Expected**:
- Test name
- Error message
- Traceback
- Module/file location

**Priority**: P0

---

### UR-UT-007: All Tests Passing

**Description**: Handle 100% pass rate correctly

**Input**:
- All tests passed

**Expected**:
- Pass rate = 100.0%
- Status = "🟢 PASS"
- No failures section

**Priority**: P0

---

### UR-UT-008: All Tests Failing

**Description**: Handle 0% pass rate correctly

**Input**:
- All tests failed

**Expected**:
- Pass rate = 0.0%
- Status = "🔴 FAIL"
- All failures listed

**Priority**: P1

---

### UR-UT-009: No Tests Run

**Description**: Handle empty test results

**Input**:
- Total tests = 0

**Expected**:
- Pass rate = 0.0%
- Status = "⚪ N/A"
- Empty module breakdown

**Priority**: P1

---

### UR-UT-010: Missing Coverage Data

**Description**: Handle missing coverage JSON

**Input**:
- pytest JSON present
- coverage JSON missing/empty

**Expected**:
- Use default coverage = 0.0%
- Log warning
- Report still generates

**Priority**: P1

---

### UR-UT-011: Test Duration Extraction

**Description**: Extract test durations if available

**Input**:
- Pytest JSON with duration field

**Expected**:
- Extract duration per test
- Calculate total duration
- Format as seconds

**Priority**: P2

---

### UR-UT-012: Module Name from Path

**Description**: Extract clean module name from file path

**Input**:
- Path: `src/nikhil/nibandha/reporting/quality.py`

**Expected**:
- Module name: "Reporting"
- Capitalized correctly
- Handles edge cases

**Priority**: P1

---

## Implementation

### Test File
`tests/unit/reporting/test_unit_report.py`

### Example Tests

```python
import pytest
from nibandha.reporting.unit import UnitDataBuilder

class TestUnitReportDataBuilder:
    """Unit tests for Unit Report data builder."""
    
    @pytest.fixture
    def builder(self):
        return UnitDataBuilder()
    
    @pytest.fixture
    def sample_pytest_json(self):
        return {
            "summary": {
                "total": 150,
                "passed": 148,
                "failed": 2,
                "skipped": 0
            },
            "tests": [
                {
                    "nodeid": "tests/unit/test_example.py::test_func",
                    "outcome": "passed",
                    "duration": 0.01
                },
                {
                    "nodeid": "tests/unit/test_example.py::test_fail",
                    "outcome": "failed",
                    "call": {
                        "longrepr": "AssertionError: expected 1 got 2"
                    }
                }
            ]
        }
    
    def test_extract_summary(self, builder, sample_pytest_json):
        """UR-UT-001: Extract summary correctly."""
        data = builder.build(sample_pytest_json, {})
        
        assert data["total_tests"] == 150
        assert data["passed"] == 148
        assert data["failed"] == 2
        assert data["skipped"] == 0
    
    def test_calculate_pass_rate(self, builder, sample_pytest_json):
        """UR-UT-002: Calculate pass rate accurately."""
        data = builder.build(sample_pytest_json, {})
        
        assert data["pass_rate"] == 98.7
    
    def test_all_tests_passing(self, builder):
        """UR-UT-007: Handle 100% pass rate."""
        perfect_json = {
            "summary": {"total": 100, "passed": 100, "failed": 0}
        }
        
        data = builder.build(perfect_json, {})
        
        assert data["pass_rate"] == 100.0
        assert data["status"] == "🟢 PASS"
    
    def test_no_tests_run(self, builder):
        """UR-UT-009: Handle empty test results."""
        empty_json = {
            "summary": {"total": 0, "passed": 0, "failed": 0}
        }
        
        data = builder.build(empty_json, {})
        
        assert data["total_tests"] == 0
        assert data["pass_rate"] == 0.0
        assert data["status"] == "⚪ N/A"
```

---

## Coverage Goal

- **Line Coverage**: 100% of unit.py data builder
- **Branch Coverage**: All conditional paths
- **Scenario Coverage**: All 12 test scenarios

---

## Integration with Common Tests

These tests **complement** common tests:

**Common tests verify**:
- Template engine renders correctly (TE-001 to TE-012)
- Visualization protocol works (VP-001 to VP-012)
- Data builder utilities work (DB-001 to DB-012)

**These tests verify**:
- Unit report specific data extraction
- Unit report specific calculations
- Unit report specific formatting

---

## See Also

- [Unit Report E2E Tests](./e2e_tests.md)
- [Common Tests](../common/)
- [Unit Report Module](../../../modules/reporting/unit_report/)
