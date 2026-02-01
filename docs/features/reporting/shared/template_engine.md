# Template Engine

## Overview

The Template Engine is responsible for rendering markdown reports from JSON data and template files. It provides a simple, declarative way to generate reports without complex logic.

## Purpose

- **Separate Data from Presentation**: JSON data can be generated independently from how it's displayed
- **Enable Customization**: Clients can provide custom templates without modifying code
- **Maintain Type Safety**: Errors for missing keys caught at render-time
- **Support Debugging**: Data can be saved as JSON for inspection

---

## Architecture

```
┌─────────────┐
│ JSON Data   │  (e.g., unit_data.json)
└──────┬──────┘
       │
       ├──→ ┌────────────────────┐
       │    │  Template Engine   │
       │    └────────┬───────────┘
       │             │
       └──────→ ┌───┴────────────────┐
                │ Template File      │  (e.g., unit_report_template.md)
                └───┬────────────────┘
                    │
                    ▼
             ┌──────────────────┐
             │ Markdown Report  │  (e.g., unit_report.md)
             └──────────────────┘
```

---

## API

### Class: `TemplateEngine`

```python
class TemplateEngine:
    """Renders markdown templates using JSON data."""
    
    def __init__(self, templates_dir: Path):
        """
        Args:
            templates_dir: Path to directory containing .md template files
        """
    
    def render(
        self, 
        template_name: str, 
        data: Dict[str, Any],
        output_path: Optional[Path] = None
    ) -> str:
        """
        Render a template with provided data.
        
        Args:
            template_name: Name of template file (e.g., "unit_report_template.md")
            data: Dictionary of key-value pairs to substitute in template
            output_path: Optional path to save rendered markdown
            
        Returns:
            Rendered markdown content
            
        Raises:
            FileNotFoundError: If template file doesn't exist
            ValueError: If required key is missing from data
        """
    
    def save_data(self, data: Dict[str, Any], data_path: Path):
        """
        Save report data as JSON for reference and debugging.
        
        Args:
            data: Dictionary of report data
            data_path: Path to save JSON file
        """
```

---

## Template Format

Templates use standard Python string formatting with `{key}` placeholders.

### Example Template

**File**: `unit_report_template.md`

```markdown
# Unit Test Report

**Date:** {date}
**Total Tests:** {total_tests}
**Passed:** {passed}
**Failed:** {failed}
**Pass Rate:** {pass_rate}%

## Status

Overall Status: {status}

## Module Breakdown

{module_breakdown}

## Failures

{failure_details}
```

### Example Data

**File**: `unit_data.json`

```json
{
  "date": "2026-01-17",
  "total_tests": 150,
  "passed": 148,
  "failed": 2,
  "pass_rate": 98.7,
  "status": "🟢 PASS",
  "module_breakdown": "| Module | Tests | Passed | Failed |\n...",
  "failure_details": "### test_complex_scenario\n```\nAssertionError...\n```"
}
```

### Rendered Output

**File**: `unit_report.md`

```markdown
# Unit Test Report

**Date:** 2026-01-17
**Total Tests:** 150
**Passed:** 148
**Failed:** 2
**Pass Rate:** 98.7%

## Status

Overall Status: 🟢 PASS

## Module Breakdown

| Module | Tests | Passed | Failed |
...

## Failures

### test_complex_scenario
```
AssertionError...
```
```

---

## Usage Examples

### Basic Usage

```python
from pathlib import Path
from nibandha.reporting.template_engine import TemplateEngine

# Initialize engine
engine = TemplateEngine(templates_dir=Path("src/nikhil/nibandha/reporting/templates"))

# Prepare data
data = {
    "date": "2026-01-17",
    "total_tests": 150,
    "passed": 148,
    "failed": 2,
    "pass_rate": 98.7,
    "status": "🟢 PASS"
}

# Render to string
content = engine.render("unit_report_template.md", data)
print(content)

# Render and save
engine.render(
    "unit_report_template.md",
    data,
    output_path=Path("report/unit_report.md")
)
```

### Saving JSON Data

```python
# Save data for debugging/reference
engine.save_data(
    data=data,
    data_path=Path("report/assets/data/unit_data.json")
)
```

### Full Reporter Example

```python
class UnitReporter:
    def __init__(self, template_engine, data_builder):
        self.engine = template_engine
        self.builder = data_builder
    
    def generate(self, pytest_json, coverage_json):
        # 1. Build structured data
        data = self.builder.build(pytest_json, coverage_json)
        
        # 2. Save JSON
        self.engine.save_data(data, Path("report/assets/data/unit_data.json"))
        
        # 3. Render report
        self.engine.render(
            "unit_report_template.md",
            data,
            output_path=Path("report/details/unit_report.md")
        )
```

---

## Error Handling

### Missing Template File

```python
engine.render("nonexistent_template.md", data)
# Raises: FileNotFoundError: Template not found: .../nonexistent_template.md
```

### Missing Key in Data

```python
# Template expects {total_tests} but data doesn't have it
data = {"date": "2026-01-17"}  # missing total_tests

engine.render("unit_report_template.md", data)
# Raises: ValueError: Template 'unit_report_template.md' requires key 'total_tests' which was not provided in data
```

### Handling Optional Keys

For truly optional keys, use empty string as default in the data:

```python
data = {
    "required_key": "value",
    "optional_key": data.get("some_value", "")  # Default to empty if missing
}
```

---

## Design Decisions

### Why Python `str.format()` Instead of Jinja2?

**Simplicity**:
- No additional dependencies
- No learning curve for template authors
- Faster rendering (no parsing overhead)

**Safety**:
- No code execution in templates
- Clear error messages for missing keys
- No risk of template injection

**Trade-offs**:
- No conditional logic in templates (handled in data builders)
- No loops in templates (handled in data builders with pre-formatted tables)

This is intentional - keeps templates declarative and moves logic to testable Python code.

---

### Why Save JSON Data?

**Debugging**: Can inspect data without re-running tests/tools

**Validation**: Can validate data structure against schemas

**Reusability**: Same data can feed multiple templates

**Testing**: Easy to create test fixtures

---

## Testing

### Unit Test Strategy

```python
def test_render_with_all_keys_present():
    """Template renders correctly when all keys are provided."""
    engine = TemplateEngine(template_dir)
    data = {"name": "Test", "value": "123"}
    result = engine.render("simple_template.md", data)
    assert "Test" in result
    assert "123" in result

def test_render_with_missing_key_raises_error():
    """Missing key raises ValueError with clear message."""
    engine = TemplateEngine(template_dir)
    data = {"name": "Test"}  # missing 'value'
    
    with pytest.raises(ValueError) as exc_info:
        engine.render("simple_template.md", data)
    
    assert "value" in str(exc_info.value)
    assert "simple_template.md" in str(exc_info.value)
```

See `docs/test/reporting/template_engine_corner_cases.md` for full test scenarios.

---

## See Also

- [Architecture Overview](./architecture.md)
- [Data Builders](./data_builders.md)
- [Data Schemas](../reporting/data_schemas.md)
- [Template Engine Corner Cases](../../test/reporting/template_engine_corner_cases.md)
