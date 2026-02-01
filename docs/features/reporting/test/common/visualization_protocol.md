# Common Tests - Visualization Protocol

## Purpose

Test core visualization protocol functionality that applies to **ALL chart types** across all reports.

---

## Test Scenarios

### VP-001: Default Provider Interface

**Description**: Default provider implements all required methods

**Input**:
- Default provider instance

**Expected**:
- Has all required methods:
  - `generate_unit_test_charts()`
  - `generate_e2e_test_charts()`
  - `generate_type_safety_charts()`
  - `generate_complexity_charts()`
  - `generate_architecture_charts()`

**Priority**: P0 (Critical)

---

### VP-002: Charts Generated Successfully

**Description**: Default provider generates PNG files

**Input**:
- Valid data for any chart type
- Valid output directory

**Expected**:
- PNG file(s) created
- Files exist at returned paths
- Valid PNG format

**Priority**: P0 (Critical)

---

### VP-003: Empty Data Handling

**Description**: Graceful handling of empty/minimal data

**Input**:
- Empty dict: `{}`
- Minimal data: `{"key": {}}`

**Expected**:
- No crashes
- Either generate empty chart or return empty dict
- Log warning if appropriate

**Priority**: P1 (High)

---

### VP-004: Missing Data Fields

**Description**: Handle missing expected data keys

**Input**:
- Data missing required fields
- Wrong key names

**Expected**:
- Handle gracefully with defaults
- Log warning
- No crash

**Priority**: P1 (High)

---

### VP-005: Invalid Output Directory

**Description**: Handle non-existent output directory

**Input**:
- Directory that doesn't exist

**Expected**:
- Create directory automatically
- Or raise clear error

**Priority**: P1 (High)

---

### VP-006: Custom Provider Implementation

**Description**: Custom provider works interchangeably

**Input**:
- Custom class implementing protocol

**Expected**:
- Type system accepts it
- Methods callable
- Returns correct format

**Priority**: P0 (Critical)

---

### VP-007: Return Value Format

**Description**: Verify return dict format

**Input**:
- Any chart generation call

**Expected**:
- Return `Dict[str, str]`
- Keys: chart names
- Values: file paths (ending in `.png`)

**Priority**: P0 (Critical)

---

### VP-008: Large Dataset Performance

**Description**: Handle large datasets efficiently

**Input**:
- 1000+ data points

**Expected**:
- Generate in < 5 seconds
- No memory issues

**Priority**: P2 (Medium)

---

### VP-009: Unicode in Data

**Description**: Chart labels with Unicode

**Input**:
- Labels with emoji, non-ASCII characters

**Expected**:
- Render correctly
- No encoding errors

**Priority**: P1 (High)

---

### VP-010: Concurrent Generation

**Description**: Thread-safe chart generation

**Input**:
- Multiple threads generating charts

**Expected**:
- All succeed
- No file conflicts
- No race conditions

**Priority**: P2 (Medium)

---

### VP-011: Error Propagation

**Description**: Errors propagate with context

**Input**:
- Provider that raises exception

**Expected**:
- Exception propagates
- Context preserved
- No silent failures

**Priority**: P1 (High)

---

### VP-012: Chart Overwrite

**Description**: Regeneration overwrites existing files

**Input**:
- Generate chart
- Regenerate with different data

**Expected**:
- Overwrite existing file
- New file reflects new data

**Priority**: P1 (High)

---

## Implementation

### Test File
`tests/unit/reporting/test_visualization_protocol_common.py`

### Example Test

```python
import pytest
from pathlib import Path
from nibandha.reporting.default_visualizer import DefaultVisualizationProvider
from nibandha.reporting.visualization_protocol import VisualizationProvider

class TestVisualizationProtocolCommon:
    """Common visualization protocol tests applying to all charts."""
    
    @pytest.fixture
    def provider(self):
        return DefaultVisualizationProvider()
    
    def test_default_provider_has_all_methods(self, provider):
        """VP-001: Default provider implements all required methods."""
        assert hasattr(provider, 'generate_unit_test_charts')
        assert hasattr(provider, 'generate_e2e_test_charts')
        assert hasattr(provider, 'generate_type_safety_charts')
        assert hasattr(provider, 'generate_complexity_charts')
        assert hasattr(provider, 'generate_architecture_charts')
    
    def test_charts_generated_successfully(self, provider, tmp_path):
        """VP-002: Charts are created as PNG files."""
        data = {"outcomes": {"passed": 10, "failed": 1}}
        
        charts = provider.generate_unit_test_charts(data, tmp_path)
        
        assert isinstance(charts, dict)
        assert len(charts) > 0
        
        for name, path in charts.items():
            assert Path(path).exists()
            assert path.endswith(".png")
    
    def test_custom_provider_implementation(self):
        """VP-006: Custom provider works interchangeably."""
        class MockProvider:
            def generate_unit_test_charts(self, data, output_dir):
                return {"mock_chart": "mock.png"}
            
            def generate_e2e_test_charts(self, data, output_dir):
                return {}
            
            def generate_type_safety_charts(self, data, output_dir):
                return {}
            
            def generate_complexity_charts(self, data, output_dir):
                return {}
            
            def generate_architecture_charts(self, data, output_dir):
                return {}
        
        # Type system should accept it
        provider: VisualizationProvider = MockProvider()
        result = provider.generate_unit_test_charts({}, Path("."))
        
        assert result == {"mock_chart": "mock.png"}
```

---

## Coverage Goal

- **Line Coverage**: 100% of default_visualizer.py core logic
- **Branch Coverage**: All error handling paths
- **Scenario Coverage**: All 12 test scenarios

---

## See Also

- [Visualization Protocol Module](../../../modules/reporting/visualization_protocol.md)
- [Report-Specific Viz Tests](../) (sibling directories)
- [Test Strategy](../test_strategy.md)
