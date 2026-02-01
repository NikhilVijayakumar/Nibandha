# Reporting Module E2E Test Scenarios

## Overview
End-to-End tests for the Reporting module verify the actual generation of reports and artifacts on the filesystem, ensuring all components work together.

## Scope
- Full report generation cycle (`generate_all`).
- Verification of generated files (Markdown reports, JSON data, Assets).
- Integration with external tools (pytest, mypy, ruff, import-linter).

## Scenarios

| ID | Scenario | Description | Type |
| :--- | :--- | :--- | :--- |
| **RPT-E2E-001** | **Unified Report Generation** | Verify `generate_all()` runs without error and produces the expected directory structure. | Positive |
| **RPT-E2E-002** | **Report Existence** | Verify that key reports (`overview.md`, `unit_report.md`, `e2e_report.md`) are created in the output directory. | Positive |
| **RPT-E2E-003** | **Quality Reports** | Verify that quality reports (`architecture`, `complexity`, `type_safety`) are generated. | Positive |
| **RPT-E2E-004** | **Visualization Assets** | Verify that PNG charts (coverage, outcomes, dependency graphs) are created in the `assets/` folder. | Positive |
| **RPT-E2E-006** | **Empty Test Results** | Verify report generation when JSON test results are empty or missing fields. | Negative |
| **RPT-E2E-007** | **Missing Tool Output** | Verify quality reporting when external tools (mypy, import-linter) produce no output or fail. | Negative |
| **RPT-E2E-008** | **Corrupt Data** | Verify generated reports handle corrupt or invalid JSON data gracefully (no crash). | Negative |
