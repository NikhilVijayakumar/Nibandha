# E2E Test Report - Module Documentation

## Overview
The E2E Test Report details the results of end-to-end functional tests, typically running scenarios that span multiple system components.

---

## Purpose
- **Analyze** E2E test execution results (from `pytest` or specialized E2E runners).
- **Track** scenario pass/fail rates.
- **Identify** slowest scenarios (performance regressions).
- **Detail** failure causes with screenshots or logs.

---

## Components

### 1. Data Builder
**File**: `src/nikhil/nibandha/reporting/e2e.py` (`E2EDataBuilder`)
**Responsibility**: Parse pytest JSON (filtered for e2e markers) or BDD output.
**See**: [data_builder.md](./data_builder.md)

### 2. Visualization
**File**: `src/nikhil/nibandha/reporting/default_visualizer.py`
**Responsibility**: Generate `e2e_status.png`, `e2e_durations.png`.
**See**: [visualization.md](./visualization.md)

### 3. Template
**File**: `src/nikhil/nibandha/reporting/templates/e2e_report_template.md`
**Responsibility**: Render markdown.
**See**: [template.md](./template.md)
