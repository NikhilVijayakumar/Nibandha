
import pytest
from unittest.mock import patch, MagicMock, ANY
from pathlib import Path
from nibandha.reporting import ReportGenerator
from nibandha.reporting.shared.application.orchestration.steps.unit_test_step import UnitTestStep
# from nibandha.configuration.domain.models.reporting_config import ReportingConfig

@pytest.fixture
def mock_orchestrator():
    with patch("nibandha.reporting.shared.application.generator.report_generator.ReportingOrchestrator") as mock:
        yield mock

def test_generate_all_uses_configured_quality_target(mock_orchestrator):
    """
    Verify that if a quality_target is configured, it is passed to ReportingContext.
    """
    # Setup
    custom_target = "src/custom/target"
    
    # Mock ReportingConfig
    config = MagicMock()
    config.output_dir = Path("/tmp/out")
    config.docs_dir = Path("/tmp/docs")
    config.quality_target = custom_target
    config.template_dir = None
    config.package_roots = None
    config.module_discovery = None
    config.project_name = "TestProject"
    config.export_formats = ["md"]
    config.doc_paths = None
    
    # Mock isinstance check
    def side_effect_isinstance(obj, class_or_tuple):
        if obj is config:
             if getattr(class_or_tuple, "__name__", "") == "ReportingConfig":
                 return True
             return False
        return isinstance(obj, class_or_tuple)

    with patch("nibandha.reporting.shared.application.generator.configuration_factory.isinstance", side_effect=side_effect_isinstance):
        generator = ReportGenerator(config=config)
    
    # Execute
    generator.generate_all(unit_target="tests/unit")
    
    # Verify
    mock_orchestrator.assert_called_once()
    context = mock_orchestrator.call_args[0][0]
    
    assert context.quality_target == custom_target

def test_generate_all_fallbacks_to_default_quality_target(mock_orchestrator):
    """
    Verify that if NO quality_target is configured, it falls back to the default.
    """
    # Setup
    generator = ReportGenerator(output_dir="/tmp/out")
    
    # Execute
    generator.generate_all(unit_target="tests/unit")
    
    # Verify
    mock_orchestrator.assert_called_once()
    context = mock_orchestrator.call_args[0][0]
    
    # Default fallback logic in ConfigurationFactory/ReportGenerator
    # If not set, it might correspond to a default path or None depending on implementation
    # In ConfigurationFactory: resolved.quality_target_default = DEFAULT_SOURCE_ROOT ('src')
    assert context.quality_target == "src"

def test_generate_all_explicit_override_quality_target(mock_orchestrator):
    """
    Verify that an explicit argument overrides the configuration.
    """
    # Setup
    config = MagicMock()
    config.output_dir = Path("/tmp/out")
    config.docs_dir = Path("/tmp/docs")
    config.quality_target = "src/ignored"
    config.template_dir = None
    config.package_roots = None
    config.module_discovery = None
    config.project_name = "TestProject"
    config.export_formats = ["md"]
    config.doc_paths = None

    def side_effect_isinstance(obj, class_or_tuple):
        if obj is config:
             if getattr(class_or_tuple, "__name__", "") == "ReportingConfig":
                 return True
             return False
        return isinstance(obj, class_or_tuple)

    with patch("nibandha.reporting.shared.application.generator.configuration_factory.isinstance", side_effect=side_effect_isinstance):
        generator = ReportGenerator(config=config)
    
    # Execute
    explicit_target = "src/override"
    generator.generate_all(unit_target="tests/unit", quality_target=explicit_target)
    
    # Verify
    mock_orchestrator.assert_called_once()
    context = mock_orchestrator.call_args[0][0]
    
    assert context.quality_target == explicit_target
