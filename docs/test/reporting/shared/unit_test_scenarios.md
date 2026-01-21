# Reporting: Shared Component Scenarios

## Overview
Tests for shared utilites: Generator, Config, and Grading.

## Scope
- `ReportGenerator` (Config Resolution).
- `Grader` (Logic).
- `ReportingConfig` (Validation).

## Scenarios

### Positive Cases
| ID | Scenario | Description |
| :--- | :--- | :--- |
| **RPT-SHR-001** | **Generator Config (Legacy)** | Init `ReportGenerator` with explicit paths. Verify internal state. |
| **RPT-SHR-002** | **Generator Config (AppConfig)** | Init with `AppConfig`. Verify `report_dir` is used. |
| **RPT-SHR-003** | **Generator Config (ReportingConfig)** | Init with `ReportingConfig`. Verify paths. |
| **RPT-SHR-004** | **Grader Logic** | Test all branches of `calculate_grade` (A/B/F boundaries). |

### Negative Cases
| ID | Scenario | Description |
| :--- | :--- | :--- |
| **RPT-SHR-NEG-001** | **Missing Config** | Init generator with NO args. Verify defaults or failure? (Defaults expected). |
