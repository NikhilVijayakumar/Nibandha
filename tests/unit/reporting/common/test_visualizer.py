import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from nibandha.reporting.shared.infrastructure.visualizers.default_visualizer import DefaultVisualizationProvider

@pytest.fixture
def mock_viz_impl():
    with patch("nibandha.reporting.shared.infrastructure.visualizers.default_visualizer.visualizer") as mock:
        yield mock

@pytest.fixture
def provider():
    return DefaultVisualizationProvider()

def test_generate_unit_test_charts_success(provider, mock_viz_impl, tmp_path):
    data = {
        "outcomes_by_module": {"A": {"pass": 1}},
        "coverage_by_module": {"A": 80.0},
        "durations": [0.1, 0.2]
    }
    
    # Mock file existence side effect (as logic checks if chart_path.exists())
    # We can't easily mock Path.exists locally inside the method without patching Path
    # Instead, let's make the mock_viz_impl function create a dummy file
    def side_effect_create(data, path):
        Path(path).touch()
        
    mock_viz_impl.plot_module_outcomes.side_effect = side_effect_create
    mock_viz_impl.plot_coverage.side_effect = side_effect_create
    mock_viz_impl.plot_test_duration_distribution.side_effect = side_effect_create
    
    charts = provider.generate_unit_test_charts(data, tmp_path)
    
    assert "unit_outcomes" in charts
    assert "unit_coverage" in charts
    assert "unit_durations" in charts
    
    mock_viz_impl.plot_module_outcomes.assert_called_once()

def test_generate_unit_test_charts_empty(provider, mock_viz_impl, tmp_path):
    # Empty data should produce no charts
    charts = provider.generate_unit_test_charts({}, tmp_path)
    assert charts == {}
    mock_viz_impl.plot_module_outcomes.assert_not_called()

def test_generate_e2e_charts(provider, mock_viz_impl, tmp_path):
    data = {"status_counts": {"pass": 1}, "scenarios": [{"name": "s1", "duration": 1}]}
    
    def side_effect_create(data, path):
        Path(path).touch()
    
    mock_viz_impl.plot_e2e_outcome.side_effect = side_effect_create
    mock_viz_impl.plot_e2e_durations.side_effect = side_effect_create
    
    charts = provider.generate_e2e_test_charts(data, tmp_path)
    
    assert "e2e_status" in charts
    assert "e2e_durations" in charts

def test_error_handling(provider, mock_viz_impl, tmp_path):
    # If plotting raises exception, it should be caught and logged
    mock_viz_impl.plot_module_outcomes.side_effect = Exception("Boom")
    
    data = {"outcomes_by_module": {"A": 1}}
    charts = provider.generate_unit_test_charts(data, tmp_path)
    
    # process might continue or return partial
    # Here outcomes fails, but others are empty, so likely returns {}
    assert "unit_outcomes" not in charts
