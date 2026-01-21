# Reporting: Unit Reporter Scenarios

## Overview
Tests for the Unit Test Reporting Sub-module (`reporting.unit`).

## Scope
- `UnitReporter` class.
- Processing of JUnit XML and Coverage JSON.
- Rendering of `unit_report_template.md`.

## Scenarios

### Positive Cases
| ID | Scenario | Description |
| :--- | :--- | :--- |
| **RPT-UNIT-001** | **Standard Generation** | Process valid JUnit XML and Coverage JSON. Verify HTML/Markdown output contains correct pass rate. |
| **RPT-UNIT-002** | **Zero Tests** | Process output with 0 tests. Verify graceful "No tests run" message. |
| **RPT-UNIT-003** | **100% Pass** | Verify "Grade A" assignment logic for perfect run. |

### Negative Cases
| ID | Scenario | Description |
| :--- | :--- | :--- |
| **RPT-UNIT-NEG-001** | **Missing Coverage** | Generate report with missing coverage.json. Verify report is generated with "N/A" for coverage sections. |
| **RPT-UNIT-NEG-002** | **Corrupt XML** | Process malformed XML. Verify exception or safe failure error log. |
