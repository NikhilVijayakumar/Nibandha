import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from nibandha.reporting.shared.infrastructure.visualizers.default_visualizer import DefaultVisualizationProvider

@pytest.fixture
def provider():
    # Instantiate the provider
    provider = DefaultVisualizationProvider()
    
    # Mock the internal plotters
    provider.unit_plotter = MagicMock()
    provider.e2e_plotter = MagicMock()
    provider.quality_plotter = MagicMock() 
    provider.hygiene_plotter = MagicMock()
    provider.security_plotter = MagicMock()
    provider.duplication_plotter = MagicMock()
    provider.encoding_plotter = MagicMock()
    provider.dependency_plotter = MagicMock()
    provider.doc_plotter = MagicMock()
    provider.perf_plotter = MagicMock()
    provider.conclusion_plotter = MagicMock()
    
    return provider

def test_generate_unit_test_charts_delegation(provider, tmp_path):
    data = {"some": "data"}
    expected_result = {"chart": "path"}
    
    # Setup mock return value
    provider.unit_plotter.plot.return_value = expected_result
    
    # Call the method
    result = provider.generate_unit_test_charts(data, tmp_path)
    
    # Verify delegation
    provider.unit_plotter.plot.assert_called_once_with(data, tmp_path)
    assert result == expected_result

def test_generate_e2e_test_charts_delegation(provider, tmp_path):
    data = {"scenarios": []}
    expected_result = {"e2e": "path"}
    
    provider.e2e_plotter.plot.return_value = expected_result
    
    result = provider.generate_e2e_test_charts(data, tmp_path)
    
    provider.e2e_plotter.plot.assert_called_once_with(data, tmp_path)
    assert result == expected_result

def test_generate_type_safety_charts_delegation(provider, tmp_path):
    data = {"errors": []}
    provider.quality_plotter.plot_type_safety.return_value = {}
    provider.generate_type_safety_charts(data, tmp_path)
    provider.quality_plotter.plot_type_safety.assert_called_once_with(data, tmp_path)

def test_generate_complexity_charts_delegation(provider, tmp_path):
    data = {"complexity": []}
    provider.quality_plotter.plot_complexity.return_value = {}
    provider.generate_complexity_charts(data, tmp_path)
    provider.quality_plotter.plot_complexity.assert_called_once_with(data, tmp_path)

def test_generate_architecture_charts_delegation(provider, tmp_path):
    data = {"arch": []}
    provider.quality_plotter.plot_architecture.return_value = {}
    provider.generate_architecture_charts(data, tmp_path)
    provider.quality_plotter.plot_architecture.assert_called_once_with(data, tmp_path)

def test_generate_dependency_charts_delegation(provider, tmp_path):
    data = {"deps": {}}
    provider.dependency_plotter.plot.return_value = {}
    provider.generate_dependency_charts(data, tmp_path)
    provider.dependency_plotter.plot.assert_called_once_with(data, tmp_path)

# Verify one of the others to ensure pattern holds
def test_generate_security_charts_delegation(provider, tmp_path):
    data = {"vulns": []}
    provider.security_plotter.plot.return_value = {}
    provider.generate_security_charts(data, tmp_path)
    provider.security_plotter.plot.assert_called_once_with(data, tmp_path)
