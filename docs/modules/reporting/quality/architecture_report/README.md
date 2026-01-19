# Architecture Report - Module Documentation

## Overview
The Architecture Report enforces clean architecture principles by verifying dependency rules using `import-linter`. It ensures layers (e.g., Domain, Infrastructure) respect defined boundaries.

---

## Purpose
- **Verify** adherence to dependency contracts (e.g., "Domain cannot import Infrastructure").
- **Visualise** compliance status.
- **Reporting** on specific contract violations.

---

## Components

### 1. Data Builder
**File**: `src/nikhil/nibandha/reporting/architecture.py` (`ArchitectureDataBuilder`)
**Responsibility**: Parse `import-linter` output strings.
**See**: [data_builder.md](./data_builder.md)

### 2. Visualization
**File**: `src/nikhil/nibandha/reporting/default_visualizer.py`
**Responsibility**: Generate `architecture_status.png`.
**See**: [visualization.md](./visualization.md)

### 3. Template
**File**: `src/nikhil/nibandha/reporting/templates/architecture_report_template.md`
**Responsibility**: Render markdown.
**See**: [template.md](./template.md)
