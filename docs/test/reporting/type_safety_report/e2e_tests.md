# Type Safety Report - E2E Tests

## Purpose
Verify the full generation loop for the Type Safety report, from mock tool output to final Markdown file.

---

## Test Scenarios

### TS-E2E-001: Full Report Generation (Happy Path)
**Description**: Generate report with synthesized mypy output.
**Setup**: Mock `mypy` running (or feed mock string to reporter).
**Execute**: `generate_type_safety_report()`.
**Verify**:
- JSON data saved in `assets/data/`.
- PNG chart saved in `assets/images/`.
- Markdown report saved in `details/`.
- Content contains expected error counts and module names.

### TS-E2E-002: Zero Errors (Pass)
**Description**: Generate report when codebase is clean.
**Input**: Mypy output "Success: no issues found".
**Verify**: 
- Status is 🟢 PASS.
- No critical errors block in details.

### TS-E2E-003: Broken Mypy Output
**Description**: Handle unexpected output format from tool.
**Input**: Garbage string or unexpected error message.
**Verify**: 
- Does not crash.
- Reports status as "Unknown" or logs parsing warning.
- Generates a fallback report.

### TS-E2E-004: Custom Template Integration
**Description**: Verify custom template handles type safety data keys.
**Setup**: Provide custom template requesting `{errors_by_category}`.
**Verify**: Rendered report includes specific category data.

---

## Implementation

**File**: `tests/e2e/reporting/type_safety/test_type_safety_e2e.py`

```python
def test_full_report_generation(generator, tmp_path):
    # Mocking the runner to return specific output
    # ...
    generator.generate_type_safety_report()
    
    report = (tmp_path / "Report/details/type_safety_report.md").read_text()
    assert "🔴 FAIL" in report
    assert "Total Errors" in report
```
