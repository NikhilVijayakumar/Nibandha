# Unit Report - Module Documentation

## Overview

The Unit Report provides comprehensive metrics and analysis of unit test execution, including test outcomes, coverage analysis, duration tracking, and failure details.

---

## Purpose

Generate a detailed markdown report from pytest unit test results and coverage data, including:
- Test execution summary (total, passed, failed, skipped)
- Pass rate and overall status
- Code coverage metrics (overall and per-module)
- Test outcome visualizations
- Module-level breakdown
- Detailed failure analysis

---

## Components

### 1. Data Builder
**File**: `src/nikhil/nibandha/reporting/unit.py` (`UnitDataBuilder`)

**Responsibility**: Transform raw pytest JSON and coverage JSON into structured data

**See**: [data_builder.md](./data_builder.md)

### 2. Visualization
**File**: `src/nikhil/nibandha/reporting/default_visualizer.py` (`generate_unit_test_charts`)

**Responsibility**: Generate test outcome pie chart

**See**: [visualization.md](./visualization.md)

### 3. Template
**File**: `src/nikhil/nibandha/reporting/templates/unit_report_template.md`

**Responsibility**: Markdown template structure

**See**: [template.md](./template.md)

---

## Data Flow

```
┌──────────────────┐
│ pytest --json    │ → unit.json
└────────┬─────────┘
         │
         ├──────────────────┐
         │                  │
         ▼                  ▼
┌─────────────────┐  ┌──────────────┐
│ Coverage JSON   │  │ Test Results │
└────────┬────────┘  └──────┬───────┘
         │                  │
         └──────┬───────────┘
                │
                ▼
       ┌─────────────────┐
       │ UnitDataBuilder │  Build structured data
       └────────┬────────┘
                │
                ├──→ unit_data.json
                │
                ├──→ VisualizationProvider → unit_outcomes.png
                │
                └──→ Template Engine → unit_report.md
```

---

## Input

### Pytest JSON
**Source**: `pytest --json-report --json-report-file=unit.json`

**Structure**:
```json
{
  "summary": {
    "total": 150,
    "passed": 148,
    "failed": 2,
    "skipped": 0
  },
  "tests": [
    {
      "nodeid": "tests/unit/test_example.py::test_func",
      "outcome": "passed",
      "duration": 0.01
    }
  ]
}
```

### Coverage JSON
**Source**: `coverage json -o coverage.json`

**Structure**:
```json
{
  "totals": {
    "percent_covered": 85.3
  },
  "files": {
    "src/module/file.py": {
      "summary": {
        "percent_covered": 92.1
      }
    }
  }
}
```

---

## Output

### Data JSON
**File**: `assets/data/unit_data.json`

**Schema**: See [data_builder.md](./data_builder.md#output-schema)

### Visualization
**Files**:
- `assets/images/unit_outcomes.png` - Pie chart of test outcomes

### Report
**File**: `details/unit_report.md`

**Sections**:
1. Header with date and summary metrics
2. Overall status indicator
3. Coverage metrics
4. Test outcomes visualization
5. Module breakdown table
6. Detailed failure information

---

## Example Usage

```python
from nibandha.reporting import ReportGenerator

generator = ReportGenerator()

# Generate unit report only
generator.generate_unit_report(target_dir="src/")

# Or generate all reports
generator.generate_all()
```

---

## Configuration

### Custom Template

```python
generator = ReportGenerator(
    template_dir="my_templates/"
)

# Provide custom unit_report_template.md
```

### Custom Visualization

```python
class MyVisualizer:
    def generate_unit_test_charts(self, data, output_dir):
        # Custom chart generation
        return {"unit_outcomes": "path/to/chart.png"}

generator = ReportGenerator(
    visualization_provider=MyVisualizer()
)
```

---

## Related Documentation

- [Data Builder Details](./data_builder.md)
- [Visualization Details](./visualization.md)
- [Template Structure](./template.md)
- [Unit Tests](../../../test/reporting/unit_report/unit_tests.md)
- [E2E Tests](../../../test/reporting/unit_report/e2e_tests.md)
