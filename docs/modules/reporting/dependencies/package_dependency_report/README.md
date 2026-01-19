# Package Dependency Report - Module Documentation

## Overview
The Package Dependency Report analyzes the **external** dependencies of the project (PyPI packages). It checks for outdated packages, security vulnerabilities, and license compliance.

---

## Purpose
- **Inventory** direct and transitive dependencies.
- **Check** for newer versions (outdated check).
- **Audit** for security vulnerabilities (e.g., using `pip-audit` or `safety`).
- **Visualize** the external dependency tree.

---

## Components

### 1. Data Builder
**File**: `src/nikhil/nibandha/reporting/packages.py` (`PackageDependencyDataBuilder`)
**Responsibility**: Run `pip list --outdated`, `pip-audit`, parse `requirements.txt`/`pyproject.toml`.
**See**: [data_builder.md](./data_builder.md)

### 2. Visualization
**File**: `src/nikhil/nibandha/reporting/default_visualizer.py`
**Responsibility**: Generate `dependency_tree.png` or `vulnerability_chart.png`.
**See**: [visualization.md](./visualization.md)

### 3. Template
**File**: `src/nikhil/nibandha/reporting/templates/package_dependency_report_template.md`
**Responsibility**: Render markdown.
**See**: [template.md](./template.md)
