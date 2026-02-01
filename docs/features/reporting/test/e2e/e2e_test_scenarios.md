# Reporting: E2E Reporter Scenarios

## Overview
Tests for the E2E Reporting Sub-module (`reporting.e2e`).

## Scope
- `E2EReporter` class.
- Processing of E2E test results (latency, screenshots).

## Scenarios

### Positive Cases
| ID | Scenario | Description |
| :--- | :--- | :--- |
| **RPT-E2E-001** | **Standard Generation** | Convert E2E JSON results into report. Verify latency charts are generated. |
| **RPT-E2E-002** | **Screenshot Embedding** | Verify that screenshot paths in JSON are correctly embedded as Markdown images. |

### Negative Cases
| ID | Scenario | Description |
| :--- | :--- | :--- |
| **RPT-E2E-NEG-001** | **Missing Screenshots** | JSON references screenshot that doesn't exist on disk. Verify report links safely (broken link icon or text). |
