# Reporting Module Architecture

## Overview

The Nibandha Reporting module has been redesigned with a **data-driven template architecture** and **protocol-based visualization system**. This design enables complete client customization while maintaining sensible defaults.

## Core Principles

1. **Data-Driven**: All report data is generated as JSON with documented schemas
2. **Template Engine**: Markdown reports are rendered from JSON data + template files
3. **Visualization Protocol**: Chart generation uses a protocol interface that clients can implement
4. **Full Customization**: Clients control both report content (templates) AND visualizations
5. **Sensible Defaults**: Works out-of-the-box without any configuration

---

## Architecture Diagram

```
┌──────────────────────┐
│   ReportGenerator    │  ← Entry point
└──────────┬───────────┘
           │
           ├──→ ┌────────────────────┐
           │    │  Data Builders     │  Generate JSON data
           │    └────────┬───────────┘
           │             │
           │             ├──→ UnitDataBuilder
           │             ├──→ E2EDataBuilder  
           │             ├──→ QualityDataBuilder
           │             └──→ SummaryDataBuilder
           │
           ├──→ ┌────────────────────────┐
           │    │ Visualization Provider │  Generate charts (Protocol-based)
           │    └────────┬───────────────┘
           │             │
           │             ├──→ DefaultVisualizationProvider (Built-in)
           │             └──→ CustomVisualizationProvider (Client-defined)
           │
           └──→ ┌────────────────────┐
                │  Template Engine   │  Render markdown
                └────────┬───────────┘
                         │
                         └──→ JSON + Template → Markdown Report
```

---

## Data Flow

```
1. Run Tests & Quality Tools
   ├──→ pytest → unit.json, e2e.json
   ├──→ coverage → coverage.json
   ├──→ mypy → type errors (parsed)
   ├──→ ruff → complexity violations (parsed)
   └──→ import-linter → architecture violations (parsed)

2. Data Builders Transform Raw Data
   ├──→ Extract metrics (pass rate, coverage, etc.)
   ├──→ Calculate statistics
   ├──→ Format markdown tables
   └──→ Generate structured JSON

3. Save JSON Data
   └──→ assets/data/*.json (documented schemas)

4. Visualization Provider Generates Charts
   ├──→ Read JSON data
   ├──→ Generate PNG charts
   └──→ Save to assets/images/

5. Template Engine Renders Reports
   ├──→ Load template file
   ├──→ Substitute JSON data
   └──→ Save to details/*.md or summary.md
```

---

## Component Responsibilities

### ReportGenerator (Core Orchestrator)

**Purpose**: Entry point that coordinates all reporters

**Responsibilities**:
- Initialize template engine
- Initialize visualization provider (default or custom)
- Create directory structure
- Coordinate all individual reporters
- Generate summary report

**Key Methods**:
- `__init__(output_dir, template_dir, visualization_provider, project_name)`
- `generate_all(unit_target, e2e_target, package_target)`

---

### Template Engine

**Purpose**: Render markdown from JSON data + template files

**Responsibilities**:
- Load template files
- Substitute placeholders with JSON data
- Save rendered markdown
- Save JSON data files for debugging/reference
- Handle missing keys with clear errors

**Key Methods**:
- `render(template_name, data, output_path) -> str`
- `save_data(data, data_path)`

**File**: `src/nikhil/nibandha/reporting/template_engine.py`

---

### Visualization Provider (Protocol)

**Purpose**: Define interface for chart generation

**Responsibilities**:
- Provide consistent API for visualization
- Allow clients to implement custom chart generation
- Return paths to generated chart files

**Protocol Methods**:
- `generate_unit_test_charts(data, output_dir) -> Dict[str, str]`
- `generate_e2e_test_charts(data, output_dir) -> Dict[str, str]`
- `generate_type_safety_charts(data, output_dir) -> Dict[str, str]`
- `generate_complexity_charts(data, output_dir) -> Dict[str, str]`
- `generate_architecture_charts(data, output_dir) -> Dict[str, str]`

**Files**:
- Protocol: `src/nikhil/nibandha/reporting/visualization_protocol.py`
- Default implementation: `src/nikhil/nibandha/reporting/default_visualizer.py`

---

### Data Builders

**Purpose**: Transform raw tool output into structured JSON

**Responsibilities**:
- Extract data from pytest JSON, coverage JSON, tool outputs
- Calculate metrics and statistics  
- Format markdown tables (module breakdowns, etc.)
- Generate structured JSON matching documented schemas

**Classes**:
- `UnitDataBuilder`: Unit test metrics
- `E2EDataBuilder`: E2E test metrics
- `QualityDataBuilder`: Type safety, complexity, architecture metrics
- `SummaryDataBuilder`: Aggregate all data for summary

**File**: `src/nikhil/nibandha/reporting/data_builders.py`

---

### Individual Reporters

**Purpose**: Generate specific report types

**Responsibilities**:
- Use data builder to create JSON
- Save JSON to `assets/data/`
- Call visualization provider to generate charts
- Call template engine to render markdown
- Save markdown to `details/`

**Classes**:
- `UnitReporter`: Unit test reports
- `E2EReporter`: E2E test reports
- `TypeSafetyReporter`: mypy reports
- `ComplexityReporter`: ruff complexity reports
- `ArchitectureReporter`: import-linter reports
- `DependencyReporter`: Module dependency reports
- `PackageReporter`: Package dependency reports

---

### Summary Reporter

**Purpose**: Generate top-level summary with overall conclusions

**Responsibilities**:
- Aggregate data from all reporters
- Calculate overall health status
- Generate priority action items
- Render `summary.md` at root level

**File**: `src/nikhil/nibandha/reporting/summary.py`

---

## Directory Structure

```
.Nibandha/Nibandha/Report/
├── summary.md                    # Top-level summary + conclusions
├── details/                      # All individual reports
│   ├── unit_report.md
│   ├── e2e_report.md
│   ├── type_safety_report.md
│   ├── complexity_report.md
│   ├── architecture_report.md
│   ├── quality_overview.md
│   ├── module_dependency_report.md
│   └── package_dependency_report.md
└── assets/                       # Non-markdown assets
    ├── images/                   # PNG visualizations
    │   ├── unit_outcomes.png
    │   ├── e2e_status.png
    │   ├── type_errors_by_module_q.png
    │   └── ...
    └── data/                     # JSON data files
        ├── unit_data.json
        ├── e2e_data.json
        ├── type_safety_data.json
        ├── complexity_data.json
        ├── architecture_data.json
        └── summary_data.json
```

---

## Customization Points

### Custom Templates

Clients can provide their own templates:

```python
generator = ReportGenerator(
    template_dir="my_custom_templates/"
)
```

Templates use standard Python string formatting with documented JSON keys:
```markdown
# Unit Test Report

**Date:** {date}
**Total Tests:** {total_tests}
**Pass Rate:** {pass_rate}%
```

See `docs/reporting/data_schemas.md` for all available keys.

---

### Custom Visualizations

Clients can implement the `VisualizationProvider` protocol:

```python
class MyCustomVisualizer:
    def generate_unit_test_charts(self, data, output_dir):
        # Use plotly, seaborn, d3, or any library
        # Generate charts from data
        # Return dict of chart names to paths
        return {"unit_outcomes": "path/to/chart.png"}
    
    # ... implement other methods

generator = ReportGenerator(
    visualization_provider=MyCustomVisualizer()
)
```

---

## Design Decisions

### Why Protocol-Based Visualizations?

- **Flexibility**: Clients can use any charting library (matplotlib, plotly, seaborn, etc.)
- **No Lock-In**: Not tied to our default visualization choices
- **Testing**: Easy to mock for testing
- **Future-Proof**: Can add new chart types without breaking changes

### Why Template Engine Instead of Code Generation?

- **Simplicity**: Templates are easier to customize than Python code
- **Separation of Concerns**: Data generation separate from presentation
- **Client Control**: Non-programmers can customize reports
- **No Code Injection**: Templates are declarative and safe

### Why JSON Intermediate Format?

- **Debugging**: Can inspect data before rendering
- **Reusability**: Same data can feed multiple templates
- **Testing**: Easy to validate structure
- **Documentation**: Schemas are clear and versioned

---

## Migration from Previous Architecture

### Old Architecture

- Reports generated directly in code
- Hard-coded template logic
- Fixed directory structure (data/ and quality/ folders)
- No customization points
- Pravaha-specific module references

### New Architecture

- Data-driven with JSON intermediate format
- Template engine for rendering
- Clean directory structure (summary.md + details/ + assets/)
- Full customization (templates + visualizations)
- Generic module detection from actual codebase

---

## See Also

- [Template Engine Documentation](./template_engine.md)
- [Visualization Protocol Documentation](./visualization_protocol.md)
- [Data Builders Documentation](./data_builders.md)
- [Data Schemas](../reporting/data_schemas.md)
- [Customization Guide](../reporting/customization_guide.md)
