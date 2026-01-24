# Unit Report - E2E Tests

## Purpose

End-to-end tests specific to **Unit Report** generation. These tests verify the complete flow from pytest/coverage execution through data transformation, visualization, and report rendering.

---

## Scope

Tests the **full integration** of:
- Data builder (pytest → JSON)
- Visualization provider (JSON → charts)
- Template engine (JSON → markdown)
- File system operations

**Note**: System-wide E2E tests are in [`system/`](../system/)

---

## Test Scenarios

### UR-E2E-001: Happy Path Generation

**Description**: Complete unit report generation with all data present

**Setup**:
- Run pytest with --json-report
- Run coverage and generate JSON
- Both have valid, complete data

**Execute**:
- `ReportGenerator().generate_unit_report()`

**Verify**:
- `details/unit_report.md` exists
- `assets/data/unit_data.json` exists
- `assets/images/unit_outcomes.png` exists
- Report contains correct metrics
- All links work

**Priority**: P0

---

### UR-E2E-002: Missing Coverage Data

**Description**: Generate report when coverage data unavailable

**Setup**:
- Pytest JSON present
- Coverage JSON missing

**Execute**:
- `generate_unit_report()`

**Verify**:
- Report still generated
- Coverage shows 0% or N/A
- Warning logged
- No crash

**Priority**: P1

---

### UR-E2E-003: All Tests Passing

**Description**: Report generation with 100% pass rate

**Setup**:
- All tests pass
- High coverage

**Execute**:
- `generate_unit_report()`

**Verify**:
- Status = "🟢 PASS"
- Pass rate = 100%
- No failures section
- Positive summary

**Priority**: P0

---

### UR-E2E-004: All Tests Failing

**Description**: Report generation with 0% pass rate

**Setup**:
- All tests fail

**Execute**:
- `generate_unit_report()`

**Verify**:
- Status = "🔴 FAIL"
- Pass rate = 0%
- All failures listed
- Critical summary

**Priority**: P1

---

### UR-E2E-005: Custom Template

**Description**: Use custom unit report template

**Setup**:
- Provide custom `unit_report_template.md`
- Custom formatting/sections

**Execute**:
- `ReportGenerator(template_dir="custom/")`

**Verify**:
- Custom template used
- All keys substituted
- Report follows custom format

**Priority**: P1

---

### UR-E2E-006: Custom Visualization

**Description**: Use custom visualization provider

**Setup**:
- Custom provider for test outcome chart

**Execute**:
- `ReportGenerator(visualization_provider=CustomProvider())`

**Verify**:
- Custom chart generated
- Chart path in report data
- Report references custom chart

**Priority**: P1

---

### UR-E2E-007: Report Regeneration

**Description**: Regenerate report overwrites existing

**Setup**:
- Generate report once
- Generate again with different data

**Execute**:
- Generate twice

**Verify**:
- Files overwritten (not duplicated)
- New data reflected
- Timestamps updated

**Priority**: P1

---

### UR-E2E-008: Large Test Suite

**Description**: Handle 1000+ tests efficiently

**Setup**:
- Pytest JSON with 1000+ tests

**Execute**:
- `generate_unit_report()`

**Verify**:
- Completes in < 10 seconds
- All data processed
- No performance issues

**Priority**: P2

---

### UR-E2E-009: Unicode in Test Names

**Description**: Handle Unicode throughout pipeline

**Setup**:
- Tests with Unicode names
- Error messages with non-ASCII

**Execute**:
- `generate_unit_report()`

**Verify**:
- All Unicode preserved
- No encoding errors
- Chart handles Unicode labels

**Priority**: P1

---

### UR-E2E-010: Verify JSON Schema

**Description**: Generated JSON matches documented schema

**Setup**:
- Standard test run

**Execute**:
- `generate_unit_report()`

**Verify**:
- `unit_data.json` validates against schema
- All required keys present
- Types correct

**Priority**: P0

---

### UR-E2E-011: Verify Image Links

**Description**: All image links in markdown work

**Setup**:
- Generate report

**Verify**:
- Parse markdown for image links
- All linked files exist
- Paths are correct (relative)

**Priority**: P0

---

### UR-E2E-012: Concurrent Generation

**Description**: Multiple reports generated concurrently

**Setup**:
- Generate unit report + e2e report simultaneously

**Execute**:
- Parallel generation

**Verify**:
- Both complete successfully
- No file conflicts
- No race conditions

**Priority**: P2

---

## Implementation

### Test File
`tests/e2e/reporting/test_unit_report_e2e.py`

### Example Tests

```python
import pytest
from pathlib import Path
from nibandha.reporting import ReportGenerator

class TestUnitReportE2E:
    """E2E tests for unit report generation."""
    
    @pytest.fixture
    def report_dir(self, tmp_path):
        return tmp_path / "report"
    
    @pytest.fixture
    def generator(self, report_dir):
        return ReportGenerator(output_dir=str(report_dir))
    
    def test_happy_path_generation(self, generator, report_dir):
        """UR-E2E-001: Complete report generation."""
        # Generate report
        generator.generate_unit_report(target_dir="src/")
        
        # Verify files exist
        assert (report_dir / "details" / "unit_report.md").exists()
        assert (report_dir / "assets" / "data" / "unit_data.json").exists()
        assert (report_dir / "assets" / "images" / "unit_outcomes.png").exists()
        
        # Verify content
        report = (report_dir / "details" / "unit_report.md").read_text()
        assert "# Unit Test Report" in report
        assert "Pass Rate" in report
    
    def test_custom_template(self, tmp_path, report_dir):
        """UR-E2E-005: Custom template usage."""
        # Create custom template
        custom_dir = tmp_path / "custom_templates"
        custom_dir.mkdir()
        custom_template = custom_dir / "unit_report_template.md"
        custom_template.write_text("# CUSTOM REPORT\n\n{status}")
        
        # Generate with custom template
        gen = ReportGenerator(
            output_dir=str(report_dir),
            template_dir=str(custom_dir)
        )
        gen.generate_unit_report(target_dir="src/")
        
        # Verify custom template used
        report = (report_dir / "details" / "unit_report.md").read_text()
        assert "# CUSTOM REPORT" in report
    
    def test_verify_json_schema(self, generator, report_dir):
        """UR-E2E-010: JSON validates against schema."""
        import json
        
        generator.generate_unit_report(target_dir="src/")
        
        # Load JSON
        data_file = report_dir / "assets" / "data" / "unit_data.json"
        data = json.loads(data_file.read_text())
        
        # Verify required keys
        required_keys = [
            "date", "total_tests", "passed", "failed",
            "pass_rate", "status", "coverage_total"
        ]
        for key in required_keys:
            assert key in data, f"Missing required key: {key}"
```

---

## Coverage Goal

- **Scenario Coverage**: All 12 E2E scenarios
- **Integration Points**: Data builder → Viz → Template → Files
- **Environment**: Works on Windows, Linux, macOS

---

## See Also

- [Unit Report Unit Tests](./unit_tests.md)
- [System E2E Tests](../system/full_generation_scenarios.md)
- [Unit Report Module](../../../modules/reporting/unit_report/)
