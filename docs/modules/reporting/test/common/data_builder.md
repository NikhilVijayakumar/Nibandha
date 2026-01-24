# Common Tests - Data Builder

## Purpose

Test core data transformation functionality that applies to **ALL data builders** (unit, e2e, type safety, complexity, architecture, summary).

---

## Test Scenarios

### DB-001: Valid JSON Parsing

**Description**: Successfully parse well-formed input JSON

**Input**:
- Valid JSON with all expected fields

**Expected**:
- Parse without errors
- Extract all fields correctly

**Priority**: P0 (Critical)

---

### DB-002: Malformed JSON Handling

**Description**: Gracefully handle malformed JSON

**Input**:
- Invalid JSON syntax
- Truncated JSON

**Expected**:
- Catch parsing error
- Return default/empty structure
- Log error

**Priority**: P1 (High)

---

### DB-003: Missing Required Fields

**Description**: Handle JSON missing expected fields

**Input**:
- JSON missing required keys
- Nested structure incomplete

**Expected**:
- Use defaults for missing fields
- Log warnings
- No crash

**Priority**: P0 (Critical)

---

### DB-004: Division by Zero

**Description**: Safe handling of zero divisors in calculations

**Input**:
- Total count = 0
- Calculate percentage/rate

**Expected**:
- Return 0.0 or appropriate default
- No `ZeroDivisionError`

**Priority**: P0 (Critical)

---

### DB-005: Empty Data Sets

**Description**: Handle empty test results/metrics

**Input**:
- Empty test list: `[]`
- No data points

**Expected**:
- Return valid structure
- Metrics show 0 or N/A
- No errors

**Priority**: P1 (High)

---

### DB-006: Unicode in Data

**Description**: Preserve Unicode in test names, errors, etc.

**Input**:
- Test names with emoji: `"test_功能_✅"`
- Error messages with non-ASCII

**Expected**:
- Preserve all characters
- No encoding errors

**Priority**: P1 (High)

---

### DB-007: Large Data Sets

**Description**: Handle datasets with 1000+ items

**Input**:
- 1000+ tests/modules/errors

**Expected**:
- Process efficiently (< 5 seconds)
- No memory issues

**Priority**: P2 (Medium)

---

### DB-008: Table Formatting

**Description**: Generate valid markdown tables

**Input**:
- Module breakdown data

**Expected**:
- Valid markdown table syntax
- Column alignment correct
- Headers present

**Priority**: P1 (High)

---

### DB-009: Empty Table Handling

**Description**: Table formatting with no data

**Input**:
- Empty module list
- No results to tabulate

**Expected**:
- Return empty table or placeholder
- Valid markdown syntax

**Priority**: P1 (High)

---

### DB-010: Special Characters in Tables

**Description**: Escape special markdown characters in table cells

**Input**:
- Module names with `|`, `-`, etc.
- Values with markdown syntax

**Expected**:
- Properly escape characters
- Table renders correctly

**Priority**: P1 (High)

---

### DB-011: Metric Calculations

**Description**: Accurate percentage/rate calculations

**Input**:
- Various pass/fail combinations

**Expected**:
- Correct percentage (rounded appropriately)
- Edge cases handled (100%, 0%, near-0%)

**Priority**: P0 (Critical)

---

### DB-012: Status Determination

**Description**: Correct status emoji based on results

**Input**:
- All passed
- Some failed
- All failed

**Expected**:
- 🟢 PASS when all passed
- 🔴 FAIL when any failed
- Consistent logic

**Priority**: P0 (Critical)

---

## Implementation

### Test File
`tests/unit/reporting/test_data_builder_common.py`

### Example Test

```python
import pytest
from nibandha.reporting.data_builders import BaseDataBuilder

class TestDataBuilderCommon:
    """Common data builder tests applying to all builders."""
    
    def test_division_by_zero_handling(self):
        """DB-004: Safe division with zero total."""
        builder = BaseDataBuilder()
        
        # This should not raise ZeroDivisionError
        rate = builder._calculate_percentage(0, 0)
        
        assert rate == 0.0
    
    def test_missing_required_fields(self):
        """DB-003: Handle missing JSON fields gracefully."""
        builder = UnitDataBuilder()
        incomplete_json = {"summary": {}}  # Missing required fields
        
        # Should not crash
        result = builder.build(incomplete_json, {})
        
        # Should have valid structure with defaults
        assert "total_tests" in result
        assert result["total_tests"] == 0
    
    def test_unicode_preservation(self):
        """DB-006: Preserve Unicode characters."""
        builder = UnitDataBuilder()
        
        data_with_unicode = {
            "summary": {"total": 1, "passed": 1},
            "tests": [
                {
                    "nodeid": "test_功能_✅",
                    "outcome": "passed"
                }
            ]
        }
        
        result = builder.build(data_with_unicode, {})
        
        # Unicode should be preserved
        assert "功能" in str(result)
        assert "✅" in str(result)
    
    def test_table_formatting_valid_markdown(self):
        """DB-008: Generate valid markdown tables."""
        builder = BaseDataBuilder()
        
        data = {
            "Module A": {"tests": 10, "passed": 9},
            "Module B": {"tests": 5, "passed": 5}
        }
        
        table = builder._format_module_table(data)
        
        # Should have headers
        assert "| Module" in table
        assert "|:---" in table or "| :---" in table
        
        # Should have data rows
        assert "Module A" in table
        assert "Module B" in table
    
    def test_metric_calculation_accuracy(self):
        """DB-011: Accurate percentage calculations."""
        builder = BaseDataBuilder()
        
        # Test various scenarios
        assert builder._calculate_percentage(50, 100) == 50.0
        assert builder._calculate_percentage(100, 100) == 100.0
        assert builder._calculate_percentage(0, 100) == 0.0
        assert builder._calculate_percentage(1, 3) == 33.3  # Rounded
```

---

## Coverage Goal

- **Line Coverage**: 100% of data_builders.py core utilities
- **Branch Coverage**: All error paths and edge cases
- **Scenario Coverage**: All 12 test scenarios

---

## See Also

- [Data Builders Module](../../../modules/reporting/data_builders.md)
- [Report-Specific Data Tests](../) (sibling directories)
- [Test Strategy](../test_strategy.md)
