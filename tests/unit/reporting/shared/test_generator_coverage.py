
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from nibandha.reporting.shared.application.generator import ReportGenerator
from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.configuration.domain.models.reporting_config import ReportingConfig
from nibandha.reporting.shared.application.orchestration.orchestrator import ReportingOrchestrator

@pytest.fixture
def mock_reporters():
    # Update patches to point to where they are imported/used (reporter_factory)
    with patch("nibandha.reporting.shared.application.generator.reporter_factory.introduction_reporter") as intro, \
         patch("nibandha.reporting.shared.application.generator.reporter_factory.unit_reporter") as unit, \
         patch("nibandha.reporting.shared.application.generator.reporter_factory.e2e_reporter") as e2e, \
         patch("nibandha.reporting.shared.application.generator.reporter_factory.quality_reporter") as qual, \
         patch("nibandha.reporting.shared.application.generator.reporter_factory.dependency_reporter") as dep, \
         patch("nibandha.reporting.shared.application.generator.reporter_factory.package_reporter") as pkg, \
         patch("nibandha.reporting.shared.application.generator.reporter_factory.documentation_reporter") as doc, \
         patch("nibandha.reporting.shared.application.generator.reporter_factory.TemplateEngine") as templ, \
         patch("nibandha.reporting.shared.application.generator.reporter_factory.DefaultVisualizationProvider") as viz, \
         patch("nibandha.reporting.shared.application.generator.reporter_factory.ReferenceCollector") as ref:
        
        yield {
            "intro": intro, "unit": unit, "e2e": e2e, "qual": qual, 
            "dep": dep, "pkg": pkg, "doc": doc, "templ": templ
        }

def test_init_defaults(mock_reporters, tmp_path):
    gen = ReportGenerator(output_dir=str(tmp_path))
    assert gen.output_dir == tmp_path
    assert gen.project_name == "Nibandha"
    assert gen.unit_target_default == "tests/unit"

def test_init_with_app_config(mock_reporters):
    config = AppConfig(name="MyApp", report_dir="custom/report")
    gen = ReportGenerator(config=config)
    
    assert gen.project_name == "MyApp"
    # Normalize path separators for comparison
    assert str(Path("custom/report").resolve()) == str(gen.output_dir)

def test_init_with_reporting_config(mock_reporters, tmp_path):
    # Ensure model is ready
    from nibandha.reporting.shared.domain.protocols.module_discovery import ModuleDiscoveryProtocol
    ReportingConfig.model_rebuild()
    
    config = ReportingConfig(
        project_name="RepApp", 
        output_dir=tmp_path / "out",
        docs_dir=tmp_path / "doc",
        quality_target="src/foo"
    )
    gen = ReportGenerator(config=config)
    
    assert gen.project_name == "RepApp"
    assert gen.quality_target_default == "src/foo"

@patch("pathlib.Path.cwd")
def test_determine_source_root_defaults(mock_cwd, mock_reporters, tmp_path):
    mock_cwd.return_value = tmp_path
    gen = ReportGenerator()
    # Should fallback to cwd/src -> tmp_path/src
    assert gen.source_root == tmp_path / "src"

@patch("pathlib.Path.cwd")
def test_determine_source_root_nested(mock_cwd, mock_reporters):
    # Logic moved to ConfigurationFactory, just ensure it runs without error
    mock_cwd.return_value = Path("/root")
    gen = ReportGenerator()
    assert gen.source_root is not None

@patch("nibandha.reporting.shared.application.generator.report_generator.ReportingOrchestrator")
def test_generate_all_flow(mock_orchestrator, mock_reporters, tmp_path):
    gen = ReportGenerator(output_dir=str(tmp_path))
    
    # Execute
    gen.generate_all()
    
    # Verify Orchestrator initialized and run
    mock_orchestrator.assert_called_once()
    instance = mock_orchestrator.return_value
    instance.run.assert_called_once()

    # Verify context and steps passed to orchestrator
    args, _ = mock_orchestrator.call_args
    context, steps = args
    assert context.project_name == "Nibandha"
    assert len(steps) > 0
