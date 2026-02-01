# Module Dependency Report - Module Documentation

## Overview
The Module Dependency Report analyzes the internal dependency graph of the project. It identifies circular dependencies, isolated modules, and visualizes the relationships between different functional areas.

---

## Purpose
- **Analyze** internal imports to build a dependency graph.
- **Detect** circular dependencies (cycles).
- **Identify** isolated (orphaned) modules.
- **Visualize** the module interaction graph.
- **Measure** coupling (fan-in/fan-out).

---

## Components

### 1. Data Builder
**File**: `src/nikhil/nibandha/reporting/dependencies.py` (`ModuleDependencyDataBuilder`)
**Responsibility**: Parse imports, build graph, detect cycles.
**See**: [data_builder.md](./data_builder.md)

### 2. Visualization
**File**: `src/nikhil/nibandha/reporting/default_visualizer.py`
**Responsibility**: Generate `module_dependencies.png`.
**See**: [visualization.md](./visualization.md)

### 3. Template
**File**: `src/nikhil/nibandha/reporting/templates/module_dependency_report_template.md`
**Responsibility**: Render markdown.
**See**: [template.md](./template.md)

---

## Data Flow

```
┌──────────────────┐
│ Source Code      │ (AST Parsing)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ DependencyBuilder│ → Graph Analysis
└────────┬─────────┘
         │
         ├──→ module_dependency_data.json
         ├──→ VisualizationProvider → module_dependencies.png
         └──→ Template Engine → module_dependency_report.md
```
