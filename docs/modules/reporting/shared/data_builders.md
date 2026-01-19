# Data Builders

## Overview

Data Builders are responsible for transforming raw tool output (pytest JSON, coverage JSON, mypy output, etc.) into structured JSON data that matches documented schemas. They handle all data extraction, metric calculation, and formatting logic.

## Purpose

- **Data Extraction**: Parse raw output from testing and quality tools
- **Metric Calculation**: Compute pass rates, coverage percentages, statistics
- **Data Structuring**: Create JSON matching documented schemas
- **Table Formatting**: Generate markdown tables for module breakdowns
- **Error Handling**: Handle missing data, malformed JSON, edge cases

---

## Architecture

```
┌──────────────────┐
│ Raw Tool Output  │  (pytest JSON, coverage JSON, mypy output, etc.)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Data Builder    │  Transform & structure
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Structured JSON  │  (matches documented schema)
└──────────────────┘
```

---

## Builder Classes

### UnitDataBuilder

**Purpose**: Transform pytest unit test results and coverage data into structured JSON.

**Input**:
- Pytest JSON report
- Coverage JSON report

**Output**: Unit test data JSON

**Key Responsibilities**:
```python
class UnitDataBuilder:
    def build(self, pytest_json: Dict, coverage_json: Dict) -> Dict[str, Any]:
        """Build structured unit test data."""
        return {
            "date": self._get_timestamp(),
            "total_tests": self._extract_total(pytest_json),
            "passed": self._extract_passed(pytest_json),
            "failed": self._extract_failed(pytest_json),
            "skipped": self._extract_skipped(pytest_json),
            "pass_rate": self._calculate_pass_rate(...),
            "status": self._determine_status(...),
            "coverage_total": self._extract_coverage(coverage_json),
            "coverage_by_module": self._extract_module_coverage(coverage_json),
            "outcomes": self._build_outcomes_dict(...),
            "module_breakdown": self._build_module_table(...),
            "failures": self._extract_failure_details(pytest_json)
        }
```

**Methods**:
- `_extract_total()`: Get total test count
- `_extract_passed()`: Get passed test count
- `_calculate_pass_rate()`: Calculate percentage
- `_determine_status()`: Return status emoji based on failures
- `_extract_coverage()`: Get overall coverage percentage
- `_extract_module_coverage()`: Get per-module coverage
- `_build_module_table()`: Format markdown table
- `_extract_failure_details()`: Parse failure info with tracebacks

**Output Schema**:
```json
{
  "date": "2026-01-17",
  "total_tests": 150,
  "passed": 148,
  "failed": 2,
  "skipped": 0,
  "pass_rate": 98.7,
  "status": "🟢 PASS",
  "coverage_total": 85.3,
  "coverage_by_module": {
    "reporting": 92.1,
    "core": 88.5
  },
  "outcomes": {
    "passed": 148,
    "failed": 2,
    "skipped": 0
  },
  "module_breakdown": "| Module | Tests | Passed | Failed |\n...",
  "failures": [
    {
      "test_name": "test_complex_scenario",
      "module": "Reporting",
      "error": "AssertionError: ...",
      "traceback": "..."
    }
  ]
}
```

---

### E2EDataBuilder

**Purpose**: Transform pytest E2E test results into structured JSON.

**Input**:
- Pytest JSON report (E2E tests)

**Output**: E2E test data JSON

**Key Responsibilities**:
```python
class E2EDataBuilder:
    def build(self, pytest_json: Dict) -> Dict[str, Any]:
        """Build structured E2E test data."""
        return {
            "date": self._get_timestamp(),
            "total_scenarios": self._extract_total(pytest_json),
            "passed": self._extract_passed(pytest_json),
            "failed": self._extract_failed(pytest_json),
            "pass_rate": self._calculate_pass_rate(...),
            "status": self._determine_status(...),
            "status_distribution": self._build_status_dict(...),
            "scenario_durations": self._extract_durations(pytest_json),
            "module_breakdown": self._build_module_table(...),
            "failures": self._extract_failure_details(pytest_json),
            "slowest_scenarios": self._get_slowest_n(pytest_json, n=10)
        }
```

**Output Schema**:
```json
{
  "date": "2026-01-17",
  "total_scenarios": 25,
  "passed": 23,
  "failed": 2,
  "pass_rate": 92.0,
  "status": "🔴 FAIL",
  "status_distribution": {
    "passed": 23,
    "failed": 2
  },
  "scenario_durations": {
    "test_scenario_1": 1.23,
    "test_scenario_2": 0.45
  },
  "module_breakdown": "| Module | Scenarios | Passing | Failing |\n...",
  "failures": [...],
  "slowest_scenarios": [...]
}
```

---

### QualityDataBuilder

**Purpose**: Transform quality tool outputs (mypy, ruff, import-linter) into structured JSON.

**Input**:
- Tool outputs (text/stdout from mypy, ruff, import-linter)
- Raw pytest quality check results

**Output**: Quality data JSON for each check type

**Key Responsibilities**:
```python
class QualityDataBuilder:
    def build_type_safety(self, mypy_output: str) -> Dict[str, Any]:
        """Build type safety report data from mypy output."""
        errors_by_module = self._parse_mypy_by_module(mypy_output)
        errors_by_category = self._parse_mypy_by_category(mypy_output)
        
        return {
            "date": self._get_timestamp(),
            "total_errors": sum(errors_by_module.values()),
            "status": self._determine_status(...),
            "errors_by_module": errors_by_module,
            "errors_by_category": errors_by_category,
            "module_breakdown": self._build_module_table(errors_by_module),
            "category_table": self._build_category_table(errors_by_category),
            "detailed_errors": self._format_errors(mypy_output)
        }
    
    def build_complexity(self, ruff_output: str) -> Dict[str, Any]:
        """Build complexity report data from ruff output."""
        violations_by_module = self._parse_ruff_by_module(ruff_output)
        
        return {
            "date": self._get_timestamp(),
            "total_violations": sum(violations_by_module.values()),
            "status": self._determine_status(...),
            "violations_by_module": violations_by_module,
            "module_breakdown": self._build_module_table(violations_by_module),
            "top_complex_functions": self._format_violations(ruff_output)
        }
    
    def build_architecture(self, importlinter_output: str) -> Dict[str, Any]:
        """Build architecture report data from import-linter output."""
        # Parse failures and violations
        ...
```

**Critical**: Generic Module Parsing

Unlike the old implementation with hardcoded Pravaha modules, the new builder **dynamically detects modules** from the actual codebase:

```python
def _parse_mypy_by_module(self, output: str) -> Dict[str, int]:
    """Parse mypy output and extract modules from file paths."""
    module_errors = {}
    
    # Pattern: path/to/file.py:line: error: message [code]
    pattern = re.compile(r"([^:]+):.*error:.*")
    
    for line in output.splitlines():
        match = pattern.search(line)
        if match:
            file_path = match.group(1)
            
            # Extract module name from path
            # src/nikhil/nibandha/reporting/quality.py → "Reporting"
            module_name = self._extract_module_from_path(file_path)
            
            module_errors[module_name] = module_errors.get(module_name, 0) + 1
    
    return module_errors

def _extract_module_from_path(self, file_path: str) -> str:
    """Extract meaningful module name from file path."""
    parts = Path(file_path).parts
    
    # Look for src/ directory and extract module
    if "src" in parts:
        src_index = parts.index("src")
        if src_index + 3 < len(parts):
            # src/nikhil/nibandha/MODULE/file.py
            return parts[src_index + 3].capitalize()
    
    # Fallback to file stem
    return Path(file_path).stem.capitalize()
```

**Output Schemas**:

Type Safety:
```json
{
  "date": "2026-01-17",
  "total_errors": 15,
  "status": "🔴 FAIL",
  "errors_by_module": {
    "Reporting": 8,
    "Quality": 5,
    "Core": 2
  },
  "errors_by_category": {
    "arg-type": 7,
    "return-value": 4
  },
  "module_breakdown": "| Module | Status | Errors |\n...",
  "category_table": "| Error Type | Count | % |\n...",
  "detailed_errors": "path/to/file.py:123: error: ..."
}
```

Complexity:
```json
{
  "date": "2026-01-17",
  "total_violations": 3,
  "status": "🔴 FAIL",
  "violations_by_module": {
    "Quality": 2,
    "Reporting": 1
  },
  "module_breakdown": "| Module | Status | Violations |\n...",
  "top_complex_functions": "..."
}
```

---

### SummaryDataBuilder

**Purpose**: Aggregate data from all reporters into summary JSON.

**Input**:
- Unit test data
- E2E test data
- Quality results
- Coverage data

**Output**: Summary data JSON

**Key Responsibilities**:
```python
class SummaryDataBuilder:
    def build(
        self,
        unit_data: Dict,
        e2e_data: Dict,
        quality_results: Dict,
        coverage_data: Dict
    ) -> Dict[str, Any]:
        """Build summary data from all sources."""
        return {
            "project_name": self.project_name,
            "date": self._get_timestamp(),
            "overall_status": self._calculate_overall_status(...),
            "unit_test": self._extract_unit_summary(unit_data),
            "e2e_test": self._extract_e2e_summary(e2e_data),
            "coverage": self._extract_coverage_summary(coverage_data),
            "quality": {
                "type_safety": self._extract_type_summary(quality_results),
                "complexity": self._extract_complexity_summary(quality_results),
                "architecture": self._extract_arch_summary(quality_results)
            },
            "action_items": self._generate_action_items(...)
        }
```

**Output Schema**:
```json
{
  "project_name": "Nibandha",
  "date": "2026-01-17 15:30:00",
  "overall_status": "🟡 NEEDS ATTENTION",
  "unit_test": {
    "status": "🟢 PASS",
    "total": 150,
    "passed": 148,
    "failed": 2,
    "pass_rate": "98.7"
  },
  "e2e_test": {...},
  "coverage": {...},
  "quality": {...},
  "action_items": "- [ ] Fix 2 failing unit tests\n..."
}
```

---

## Usage Example

```python
from nibandha.reporting.data_builders import UnitDataBuilder

# Load raw data
pytest_json = load_json("unit.json")
coverage_json = load_json("coverage.json")

# Build structured data
builder = UnitDataBuilder()
unit_data = builder.build(pytest_json, coverage_json)

# unit_data is now a dictionary matching the schema
# Can be saved as JSON or passed to template engine
```

---

## Error Handling

### Missing Data

```python
def _extract_passed(self, pytest_json: Dict) -> int:
    """Extract passed count with safe fallback."""
    try:
        return pytest_json["summary"]["passed"]
    except (KeyError, TypeError):
        logger.warning("Missing 'passed' field in pytest JSON")
        return 0
```

### Division by Zero

```python
def _calculate_pass_rate(self, passed: int, total: int) -> float:
    """Calculate pass rate safely."""
    if total == 0:
        return 0.0
    return round((passed / total) * 100, 1)
```

### Malformed JSON

```python
def build(self, pytest_json: Dict, coverage_json: Dict) -> Dict[str, Any]:
    """Build with validation."""
    try:
        # Validate required fields exist
        self._validate_pytest_json(pytest_json)
        self._validate_coverage_json(coverage_json)
        
        # Build data
        return {...}
    except ValidationError as e:
        logger.error(f"Invalid input data: {e}")
        # Return minimal valid structure
        return self._get_empty_structure()
```

---

## Testing

### Unit Test Strategy

```python
def test_build_with_valid_data():
    """Builder produces correct structure with valid input."""
    builder = UnitDataBuilder()
    pytest_json = load_fixture("unit_results_all_passing.json")
    coverage_json = load_fixture("coverage_full.json")
    
    result = builder.build(pytest_json, coverage_json)
    
    assert result["total_tests"] == 150
    assert result["passed"] == 150
    assert result["pass_rate"] == 100.0
    assert result["status"] == "🟢 PASS"

def test_calculate_pass_rate_with_zero_total():
    """Pass rate calculation handles zero total."""
    builder = UnitDataBuilder()
    rate = builder._calculate_pass_rate(0, 0)
    assert rate == 0.0

def test_handle_malformed_json():
    """Builder handles malformed input gracefully."""
    builder = UnitDataBuilder()
    bad_json = {"summary": None}  # Missing required fields
    
    result = builder.build(bad_json, {})
    
    # Should return valid structure with defaults
    assert "total_tests" in result
    assert result["total_tests"] == 0
```

See `docs/test/reporting/data_builders_corner_cases.md` for comprehensive test scenarios.

---

## See Also

- [Architecture Overview](./architecture.md)
- [Template Engine](./template_engine.md)
- [Data Schemas](../reporting/data_schemas.md)
- [Data Builders Corner Cases](../../test/reporting/data_builders_corner_cases.md)
