# Common Tests - Overview

## Purpose

This directory contains test scenarios for **core components** that apply to **ALL reports**. These tests verify general functionality independent of specific report types.

---

## Components Tested

### 1. Template Engine (`template_engine.md`)

**What it tests**: Core template rendering functionality

**Applies to**: All reports (unit, e2e, type safety, complexity, architecture, summary)

**Test scenarios**:
- Template file handling (missing files, empty templates)
- Data substitution (missing keys, extra keys, special characters)
- Edge cases (Unicode, large data, concurrent rendering)
- JSON data saving

---

### 2. Visualization Protocol (`visualization_protocol.md`)

**What it tests**: Core visualization generation functionality

**Applies to**: All chart types across all reports

**Test scenarios**:
- Default provider functionality
- Custom provider implementation
- Empty/missing data handling
- Error propagation
- Concurrent generation

---

### 3. Data Builder (`data_builder.md`)

**What it tests**: Core data transformation functionality

**Applies to**: All data builders

**Test scenarios**:
- JSON parsing (malformed input, missing fields)
- Metric calculations (division by zero, edge cases)
- Table formatting (empty data, special characters)
- Error handling (validation, defaults)

---

## Relationship to Report-Specific Tests

```
Common Tests (General)
    ↓
    Tests core functionality that ALL reports use
    ↓
    Example: "Template engine handles missing keys correctly"
    
Report-Specific Tests
    ↓
    Tests functionality unique to each report
    ↓
    Example: "Unit report calculates pass rate correctly"
```

**Common tests answer**: "Does the engine/protocol/builder work correctly in general?"

**Report-specific tests answer**: "Does this specific report generate correctly with its unique data?"

---

## Test Organization

### What Goes in Common Tests

✅ Template engine core functionality (render, save_data, error handling)
✅ Visualization protocol interface (default/custom providers, error handling)
✅ Data builder core utilities (parsing, validation, formatting)
✅ Edge cases that apply to all components (Unicode, empty data, concurrency)

### What Goes in Report-Specific Tests

❌ Report-specific data extraction (e.g., pytest JSON parsing for unit tests)
❌ Report-specific calculations (e.g., pass rate, coverage percentages)
❌ Report-specific visualizations (e.g., test outcome pie chart)
❌ Report-specific template keys (e.g., `{total_tests}`, `{pass_rate}`)

---

## Files in This Directory

1. **README.md** (this file) - Overview of common tests
2. **template_engine.md** - Template engine core tests
3. **visualization_protocol.md** - Visualization protocol core tests
4. **data_builder.md** - Data builder core tests

---

## See Also

- [Test Strategy](../test_strategy.md)
- [Report-Specific Tests](../) (sibling directories)
- [Module Documentation](../../modules/reporting/)
