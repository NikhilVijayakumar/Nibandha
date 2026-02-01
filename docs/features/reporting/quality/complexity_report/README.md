# Complexity Report - Module Documentation

## Overview
The Complexity Report analyzes code complexity using `ruff` (specifically McCabe cyclomatic complexity). It highlights functions or modules that are overly complex and hard to maintain.

---

## Purpose
- **Parse** `ruff` output for complexity violations (C901).
- **Identify** complex modules and functions.
- **Visualize** complexity distribution.
- **Track** technical debt related to code structure.

---

## Components

### 1. Data Builder
**File**: `src/nikhil/nibandha/reporting/complexity.py` (`ComplexityDataBuilder`)
**Responsibility**: Parse ruff layout/complexity errors.
**See**: [data_builder.md](./data_builder.md)

### 2. Visualization
**File**: `src/nikhil/nibandha/reporting/default_visualizer.py`
**Responsibility**: Generate `complexity_distribution.png`.
**See**: [visualization.md](./visualization.md)

### 3. Template
**File**: `src/nikhil/nibandha/reporting/templates/complexity_report_template.md`
**Responsibility**: Render markdown.
**See**: [template.md](./template.md)

---

## Data Flow

```
┌──────────────────┐
│ ruff stdout      │ (C901 violations)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ ComplexityBuilder│
└────────┬─────────┘
         │
         ├──→ complexity_data.json
         ├──→ VisualizationProvider → complexity_distribution.png
         └──→ Template Engine → complexity_report.md
```
