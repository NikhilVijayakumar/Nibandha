
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from nibandha.reporting import ReportGenerator
# from nibandha.configuration.domain.models.reporting_config import ReportingConfig

@pytest.fixture
def mock_run_pytest():
    with patch("nibandha.reporting.shared.infrastructure.utils.run_pytest") as mock:
        yield mock

def test_run_unit_tests_uses_configured_coverage_target(mock_run_pytest):
    """
    Verify that if a quality_target is configured, it is passed to run_pytest as the coverage target.
    """
    # Setup
    custom_target = "src/custom/target"
    
    # Mock ReportingConfig to avoid Pydantic issues
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
    
    # Mock isinstance check to distinguish AppConfig vs ReportingConfig
    # We want isinstance(config, AppConfig) -> False
    # and isinstance(config, ReportingConfig) -> True
    def side_effect_isinstance(obj, class_or_tuple):
        if obj is config:
             # We want it to be ReportingConfig
             # But we can't perform actual check against Real ReportingConfig if pydantic fails
             # So we check against the name of class_or_tuple?
             # class_or_tuple might be the class object.
             if getattr(class_or_tuple, "__name__", "") == "ReportingConfig":
                 return True
             return False
        return isinstance(obj, class_or_tuple)

    with patch("nibandha.reporting.shared.application.generator.isinstance", side_effect=side_effect_isinstance):
        generator = ReportGenerator(config=config)
    
    # Mock unit_reporter to avoid JSON serialization of mocks
    generator.unit_reporter = MagicMock()
    
    # Execute
    generator.run_unit_Tests("tests/unit", "2024-01-01")
    
    # Verify
    mock_run_pytest.assert_called_once()
    call_args = mock_run_pytest.call_args
    # signature: run_pytest(target, json_path, cov_target)
    assert call_args[0][2] == custom_target

def test_run_unit_tests_fallbacks_to_default(mock_run_pytest):
    """
    Verify that if NO quality_target is configured, it falls back to the default package path.
    """
    # Setup
    generator = ReportGenerator(output_dir="/tmp/out")
    generator.unit_reporter = MagicMock()
    # Verify default is set correctly in init
    assert generator.quality_target_default == "src" # Default for vanilla init
    
    # BUT wait, the bug fix logic was: 
    # cov_target = self.quality_target_default or "src/nikhil/nibandha"
    # If initialized without config, quality_target_default is "src" (from _resolve_configuration -> defaults)
    
    # Let's verify what happens with vanilla init
    generator.run_unit_Tests("tests/unit", "2024-01-01")
    
    # Verify
    mock_run_pytest.assert_called_once()
    call_args = mock_run_pytest.call_args
    # Should use "src" as that's the default set in _resolve_configuration for vanilla init
    assert call_args[0][2] == "src"

def test_run_unit_tests_explicit_override(mock_run_pytest):
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

    with patch("nibandha.reporting.shared.application.generator.isinstance", side_effect=side_effect_isinstance):
        generator = ReportGenerator(config=config)
    
    generator.unit_reporter = MagicMock()
    
    # Execute
    explicit_target = "src/override"
    generator.run_unit_Tests("tests/unit", "2024-01-01", cov_target=explicit_target)
    
    # Verify
    mock_run_pytest.assert_called_once()
    assert mock_run_pytest.call_args[0][2] == explicit_target
