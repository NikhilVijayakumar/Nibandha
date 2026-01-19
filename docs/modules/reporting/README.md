# Reporting Module

## Overview
The Reporting module provides a complete solution for generating quality, unit, and end-to-end test reports. It aggregates data from various tools (pytest, mypy, ruff, import-linter) and renders professional Markdown reports with visualizations.

## Features
- **Unified Reporting**: Generates Unit, E2E, and Quality reports in one go.
- **Visualizations**: Includes charts for test outcomes, coverage, duration, and error distribution.
- **Customizable**: Supports custom templates and output directories.
- **Optional Dependencies**: Requires `[reporting]` install extras.

## Usage

### Installation
Ensure you install Nibandha with reporting extras:
```bash
pip install nibandha[reporting]
```

### Basic Generation
```python
from nibandha.reporting import ReportGenerator

# Initialize generator
generator = ReportGenerator(
    output_dir=".Nibandha/Report",
    docs_dir="docs/test"
)

# Run all checks and generate reports
generator.generate_all()
```

### Configuration
You can customize the output location and templates:
```python
generator = ReportGenerator(
    output_dir="/path/to/reports",
    template_dir="/path/to/custom/templates"
)
```

## Reports Generated
- **Unit Report**: [Unit Reporting](unit/README.md) (Test results, coverage, durations)
- **E2E Report**: [E2E Reporting](e2e/README.md) (Scenario results, latency)
- **Quality Reports**: [Quality Reporting](quality/README.md)
    - `type_safety_report.md` (mypy results)
    - `complexity_report.md` (ruff complexity)
    - `architecture_report.md` (import-linter compliance)
    - `quality_overview.md` (Overall health)
- **Dependency Reports**: [Dependency Reporting](dependencies/README.md)
    - `module_dependency_report.md` (Internal module dependencies & cycles)
    - `package_dependency_report.md` (Outdated/Unused PyPI packages)

## Shared Components
- [Template Engine](shared/template_engine.md)
- [Visualization Protocol](shared/visualization_protocol.md)
- [Data Builders](shared/data_builders.md)
