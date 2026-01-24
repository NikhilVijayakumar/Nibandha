# Common Tests - Template Engine

## Purpose

Test core template rendering functionality that applies to **ALL reports** (unit, e2e, type safety, complexity, architecture, summary).

---

## Test Scenarios

### TE-001: Successful Rendering

**Description**: Template renders correctly when all keys are present

**Input**:
- Template: `"# {title}\n\n**Status**: {status}"`
- Data: `{"title": "Test Report", "status": "PASS"}`

**Expected**:
- Renders without errors
- All placeholders replaced
- Output matches expected format

**Priority**: P0 (Critical)

---

### TE-002: Missing Key Error

**Description**: Clear error when template key missing from data

**Input**:
- Template references `{missing_key}`
- Data doesn't contain `missing_key`

**Expected**:
- Raise `ValueError`
- Error message includes:
  - Template name
  - Missing key name

**Priority**: P0 (Critical)

---

### TE-003: Extra Keys Ignored

**Description**: Extra data keys don't cause errors

**Input**:
- Template uses 2 keys
- Data has 10 keys

**Expected**:
- Render successfully
- Ignore unused keys
- No warnings

**Priority**: P1 (High)

---

### TE-004: Unicode Support

**Description**: Handle Unicode in templates and data

**Input**:
- Template with emoji and non-ASCII: `"Status: {status} 测试"`
- Data with Unicode: `{"status": "🟢 PASS"}`

**Expected**:
- Render correctly
- Preserve all Unicode characters
- Save with UTF-8 encoding

**Priority**: P0 (Critical)

---

### TE-005: Large Data Performance

**Description**: Acceptable performance with large data dictionaries

**Input**:
- Data with 1000+ keys
- Template uses 10 keys

**Expected**:
- Render in < 1 second
- No memory issues

**Priority**: P2 (Medium)

---

### TE-006: Directory Creation

**Description**: Create nested directories for output

**Input**:
- Output path: `report/deep/nested/file.md`
- Directories don't exist

**Expected**:
- Create all parent directories
- Save file successfully

**Priority**: P1 (High)

---

### TE-007: Empty Template

**Description**: Handle empty template files

**Input**:
- Template file is empty
- Valid data provided

**Expected**:
- Return empty string
- No errors

**Priority**: P2 (Medium)

---

### TE-008: JSON Data Saving

**Description**: save_data() creates valid JSON

**Input**:
- Complex nested data structure

**Expected**:
- Create JSON file
- Valid JSON format
- UTF-8 encoding
- Indented for readability

**Priority**: P0 (Critical)

---

### TE-009: Special Characters in Values

**Description**: Data values with special formatting chars

**Input**:
- Data value: `"Text with {braces} and % signs"`

**Expected**:
- Render literally
- No format string interpretation

**Priority**: P1 (High)

---

### TE-010: Newlines Preserved

**Description**: Multi-line data values preserved

**Input**:
- Data: `{"content": "Line 1\nLine 2\n  Indented"}`

**Expected**:
- Preserve newlines
- Preserve indentation

**Priority**: P1 (High)

---

### TE-011: Concurrent Rendering

**Description**: Thread-safe rendering

**Input**:
- 10 concurrent threads rendering

**Expected**:
- All render successfully
- No race conditions
- No corrupted output

**Priority**: P2 (Medium)

---

### TE-012: Template Not Found

**Description**: Clear error for missing template

**Input**:
- Non-existent template name

**Expected**:
- Raise `FileNotFoundError`
- Include full path in message

**Priority**: P0 (Critical)

---

## Implementation

### Test File
`tests/unit/reporting/test_template_engine_common.py`

### Example Test

```python
import pytest
from nibandha.reporting.template_engine import TemplateEngine

class TestTemplateEngineCommon:
    """Common template engine tests applying to all reports."""
    
    @pytest.fixture
    def engine(self, tmp_path):
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        return TemplateEngine(template_dir)
    
    def test_successful_rendering(self, engine, tmp_path):
        """TE-001: Template renders with all keys present."""
        # Create template
        template = tmp_path / "templates" / "test.md"
        template.write_text("# {title}\n\n**Status**: {status}")
        
        # Render
        data = {"title": "Test Report", "status": "PASS"}
        result = engine.render("test.md", data)
        
        # Verify
        assert "# Test Report" in result
        assert "**Status**: PASS" in result
    
    def test_missing_key_error(self, engine, tmp_path):
        """TE-002: Clear error for missing keys."""
        template = tmp_path / "templates" / "test.md"
        template.write_text("{missing_key}")
        
        with pytest.raises(ValueError) as exc_info:
            engine.render("test.md", {})
        
        assert "missing_key" in str(exc_info.value)
        assert "test.md" in str(exc_info.value)
```

---

## Coverage Goal

- **Line Coverage**: 100% of template_engine.py
- **Branch Coverage**: All error paths
- **Scenario Coverage**: All 12 test scenarios

---

## See Also

- [Template Engine Module](../../../modules/reporting/template_engine.md)
- [Report-Specific Template Tests](../) (sibling directories)
- [Test Strategy](../test_strategy.md)
