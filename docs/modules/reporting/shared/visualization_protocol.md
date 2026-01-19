# Visualization Protocol

## Overview

The Visualization Protocol defines an interface for chart generation that allows clients to provide custom visualization implementations. This enables complete freedom in choosing charting libraries and styling.

## Purpose

- **Flexibility**: Clients can use any charting library (matplotlib, plotly, seaborn, altair, d3, etc.)
- **No Lock-In**: Not tied to default visualization choices
- **Testability**: Easy to mock for testing
- **Future-Proof**: Can add new chart types without breaking existing implementations

---

## Architecture

```
┌──────────────────────────────┐
│  VisualizationProvider       │  ← Protocol (Interface)
│  (Protocol)                   │  
└──────────────┬───────────────┘
               │
               ├──→ ┌────────────────────────────────┐
               │    │ DefaultVisualizationProvider   │  ← Built-in implementation
               │    │ (uses matplotlib)              │
               │    └────────────────────────────────┘
               │
               └──→ ┌────────────────────────────────┐
                    │ CustomVisualizationProvider    │  ← Client implementation
                    │ (uses plotly, seaborn, etc.)   │
                    └────────────────────────────────┘
```

---

## Protocol Definition

### `VisualizationProvider` Protocol

```python
from typing import Protocol, Dict, Any
from pathlib import Path

class VisualizationProvider(Protocol):
    """
    Protocol for generating report visualizations.
    
    Clients can implement this protocol to provide custom visualizations.
    All methods should:
    - Accept data dictionary and output directory
    - Generate visualization(s) as PNG files
    - Return dictionary mapping chart names to file paths
    """
    
    def generate_unit_test_charts(
        self, 
        data: Dict[str, Any], 
        output_dir: Path
    ) -> Dict[str, str]:
        """
        Generate unit test visualization charts.
        
        Args:
            data: Unit test data dictionary (see data schema)
            output_dir: Directory to save PNG chart files
            
        Returns:
            Dictionary mapping chart names to file paths
            Example: {"unit_outcomes": "/path/to/unit_outcomes.png"}
        """
        ...
    
    def generate_e2e_test_charts(
        self, 
        data: Dict[str, Any], 
        output_dir: Path
    ) -> Dict[str, str]:
        """
        Generate E2E test visualization charts.
        
        Args:
            data: E2E test data dictionary
            output_dir: Directory to save chart files
            
        Returns:
            Dictionary mapping chart names to file paths
        """
        ...
    
    def generate_type_safety_charts(
        self, 
        data: Dict[str, Any], 
        output_dir: Path
    ) -> Dict[str, str]:
        """
        Generate type safety visualization charts.
        
        Args:
            data: Type safety data dictionary
            output_dir: Directory to save chart files
            
        Returns:
            Dictionary mapping chart names to file paths
        """
        ...
    
    def generate_complexity_charts(
        self, 
        data: Dict[str, Any], 
        output_dir: Path
    ) -> Dict[str, str]:
        """
        Generate complexity visualization charts.
        
        Args:
            data: Complexity data dictionary
            output_dir: Directory to save chart files
            
        Returns:
            Dictionary mapping chart names to file paths
        """
        ...
    
    def generate_architecture_charts(
        self, 
        data: Dict[str, Any], 
        output_dir: Path
    ) -> Dict[str, str]:
        """
        Generate architecture visualization charts.
        
        Args:
            data: Architecture data dictionary
            output_dir: Directory to save chart files
            
        Returns:
            Dictionary mapping chart names to file paths
        """
        ...
```

---

## Default Implementation

### `DefaultVisualizationProvider`

The built-in implementation uses matplotlib through the existing `visualizer` module.

```python
from pathlib import Path
from typing import Dict, Any
from . import visualizer

class DefaultVisualizationProvider:
    """
    Default implementation of visualization generation.
    Uses matplotlib via the built-in visualizer module.
    """
    
    def generate_unit_test_charts(
        self, 
        data: Dict[str, Any], 
        output_dir: Path
    ) -> Dict[str, str]:
        """Generate unit test charts using matplotlib."""
        charts = {}
        
        # Extract data
        outcomes = data.get("outcomes", {})
        
        # Generate test outcomes pie chart
        chart_path = output_dir / "unit_outcomes.png"
        visualizer.plot_test_outcomes(outcomes, chart_path)
        charts["unit_outcomes"] = str(chart_path)
        
        return charts
    
    def generate_e2e_test_charts(
        self, 
        data: Dict[str, Any], 
        output_dir: Path
    ) -> Dict[str, str]:
        """Generate E2E test charts."""
        charts = {}
        
        # Status distribution chart
        status_data = data.get("status_distribution", {})
        status_path = output_dir / "e2e_status.png"
        visualizer.plot_e2e_status(status_data, status_path)
        charts["e2e_status"] = str(status_path)
        
        # Duration chart
        durations = data.get("scenario_durations", {})
        duration_path = output_dir / "e2e_durations.png"
        visualizer.plot_e2e_durations(durations, duration_path)
        charts["e2e_durations"] = str(duration_path)
        
        return charts
    
    # ... other methods follow same pattern
```

---

## Custom Implementation Example

### Using Plotly

```python
from pathlib import Path
from typing import Dict, Any
import plotly.graph_objects as go

class PlotlyVisualizationProvider:
    """Custom visualization provider using Plotly."""
    
    def generate_unit_test_charts(
        self, 
        data: Dict[str, Any], 
        output_dir: Path
    ) -> Dict[str, str]:
        """Generate interactive Plotly charts."""
        charts = {}
        
        # Extract data
        outcomes = data.get("outcomes", {})
        
        # Create plotly pie chart
        fig = go.Figure(data=[go.Pie(
            labels=list(outcomes.keys()),
            values=list(outcomes.values()),
            hole=0.3
        )])
        
        fig.update_layout(
            title="Unit Test Outcomes",
            showlegend=True
        )
        
        # Save as static PNG
        chart_path = output_dir / "unit_outcomes.png"
        fig.write_image(str(chart_path))
        charts["unit_outcomes"] = str(chart_path)
        
        return charts
    
    # ... implement other methods
```

### Using Seaborn

```python
import seaborn as sns
import matplotlib.pyplot as plt

class SeabornVisualizationProvider:
    """Custom visualization provider using Seaborn."""
    
    def generate_type_safety_charts(
        self, 
        data: Dict[str, Any], 
        output_dir: Path
    ) -> Dict[str, str]:
        """Generate seaborn-styled charts."""
        charts = {}
        
        # Set seaborn style
        sns.set_theme(style="whitegrid")
        
        # Extract errors by module
        errors_by_module = data.get("errors_by_module", {})
        
        # Create bar plot
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(
            x=list(errors_by_module.keys()),
            y=list(errors_by_module.values()),
            palette="viridis",
            ax=ax
        )
        ax.set_title("Type Errors by Module", fontsize=16)
        ax.set_xlabel("Module", fontsize=12)
        ax.set_ylabel("Error Count", fontsize=12)
        plt.xticks(rotation=45)
        
        # Save
        chart_path = output_dir / "type_errors_by_module_q.png"
        fig.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        
        charts["type_errors_by_module"] = str(chart_path)
        
        return charts
```

---

## Usage

### Using Default Provider (No Configuration)

```python
from nibandha.reporting import ReportGenerator

# Default provider is used automatically
generator = ReportGenerator()
generator.generate_all()
```

### Using Custom Provider

```python
from nibandha.reporting import ReportGenerator
from my_viz import PlotlyVisualizationProvider

# Provide custom visualization provider
generator = ReportGenerator(
    visualization_provider=PlotlyVisualizationProvider()
)
generator.generate_all()
```

### In Reporter Code

```python
class UnitReporter:
    def __init__(self, viz_provider):
        self.viz_provider = viz_provider
    
    def generate(self, data):
        # Generate charts
        chart_paths = self.viz_provider.generate_unit_test_charts(
            data=data,
            output_dir=Path("report/assets/images")
        )
        
        # chart_paths now contains:
        # {"unit_outcomes": "/path/to/unit_outcomes.png"}
        
        # Use paths in report data for linking
        data["chart_paths"] = chart_paths
```

---

## Data Schemas

Each chart generation method receives a data dictionary with a documented schema.

### Unit Test Charts Data

```json
{
  "outcomes": {
    "passed": 148,
    "failed": 2,
    "skipped": 0
  },
  "coverage_by_module": {
    "reporting": 92.1,
    "core": 88.5
  }
}
```

### E2E Test Charts Data

```json
{
  "status_distribution": {
    "passed": 23,
    "failed": 2
  },
  "scenario_durations": {
    "test_scenario_1": 1.23,
    "test_scenario_2": 0.45
  }
}
```

### Type Safety Charts Data

```json
{
  "errors_by_module": {
    "Reporting": 8,
    "Quality": 5
  },
  "errors_by_category": {
    "arg-type": 7,
    "return-value": 4
  }
}
```

See `docs/reporting/data_schemas.md` for complete schemas.

---

## Design Decisions

### Why Protocol Instead of Abstract Base Class?

**Python 3.8+ Protocols** provide:
- **Structural subtyping**: No need to inherit
- **Duck typing**: Any class with matching methods works
- **Better type checking**: mypy can verify implementations
- **Flexibility**: Clients don't need to import base class

```python
# No inheritance required!
class MyVizProvider:  # Doesn't inherit from anything
    def generate_unit_test_charts(self, data, output_dir):
        # Implementation
        pass
    
    # ... other methods

# Works! mypy verifies it matches the protocol
provider: VisualizationProvider = MyVizProvider()
```

### Why Return Dict of Paths?

**Referenceability**: Reports can reference specific charts by name

**Flexibility**: Number of charts can vary

**Debugging**: Can verify which charts were generated

**Future-Proof**: Can add new charts without changing API

---

## Testing

### Unit Test Strategy

```python
def test_default_provider_generates_unit_charts(tmp_path):
    """Default provider generates PNG files."""
    provider = DefaultVisualizationProvider()
    data = {
        "outcomes": {"passed": 10, "failed": 1}
    }
    
    charts = provider.generate_unit_test_charts(data, tmp_path)
    
    assert "unit_outcomes" in charts
    assert Path(charts["unit_outcomes"]).exists()
    assert charts["unit_outcomes"].endswith(".png")

def test_custom_provider_can_replace_default():
    """Custom provider works interchangeably."""
    class MockProvider:
        def generate_unit_test_charts(self, data, output_dir):
            return {"unit_outcomes": "mock.png"}
    
    provider: VisualizationProvider = MockProvider()
    result = provider.generate_unit_test_charts({}, Path("."))
    
    assert result == {"unit_outcomes": "mock.png"}
```

See `docs/test/reporting/visualization_corner_cases.md` for comprehensive test scenarios.

---

## See Also

- [Architecture Overview](./architecture.md)
- [Template Engine](./template_engine.md)
- [Data Schemas](../reporting/data_schemas.md)
- [Visualization Corner Cases](../../test/reporting/visualization_corner_cases.md)
- [Customization Guide](../reporting/customization_guide.md)
