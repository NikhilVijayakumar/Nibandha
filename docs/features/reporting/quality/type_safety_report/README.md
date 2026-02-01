# Type Safety Report - Module Documentation

## Overview
The Type Safety Report analyzes the codebase using `mypy` to enforce static type checking. It provides a detailed breakdown of type errors by module and category, helping developers identify and prioritize type-related technical debt.

---

## Purpose
- **Analyze** output from `mypy --strict` (or configured flags).
- **Categorize** errors (e.g., `arg-type`, `return-value`, `import-untyped`).
- **Attribute** errors to specific Nibandha modules (dynamically detected).
- **Visualize** the distribution of errors to highlight hotspots.
- **Report** critical errors (Any types, missing stubs) directly.

---

## Components

### 1. Data Builder
**File**: `src/nikhil/nibandha/reporting/type_safety.py` (`TypeSafetyDataBuilder`)
**Responsibility**: Parse mypy stdout, extract error metadata, and structure JSON.
**See**: [data_builder.md](./data_builder.md)

### 2. Visualization
**File**: `src/nikhil/nibandha/reporting/default_visualizer.py`
**Responsibility**: Generate `type_errors_by_module.png`.
**See**: [visualization.md](./visualization.md)

### 3. Template
**File**: `src/nikhil/nibandha/reporting/templates/type_safety_report_template.md`
**Responsibility**: Render strict markdown report.
**See**: [template.md](./template.md)

---

## Data Flow

```
┌──────────────────┐
│ mypy stdout      │ → Raw text
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ TypeSafetyBuilder│ → Regex Parsing
└────────┬─────────┘
         │
         ├──→ type_safety_data.json
         │
         ├──→ VisualizationProvider → type_errors_by_module.png
         │
         └──→ Template Engine → type_safety_report.md
```

---

## Example Output
See `Pravaha/Report/data/type_safety_report.md` for a real-world example.
