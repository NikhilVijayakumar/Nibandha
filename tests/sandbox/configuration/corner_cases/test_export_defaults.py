
import pytest
from pathlib import Path
from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.configuration.infrastructure.file_loader import FileConfigLoader
from tests.sandbox.configuration.utils import run_config_test

def test_export_default_inheritance(sandbox_root: Path):
    loader = FileConfigLoader()
    # Configuration with no export.input_dir specified (should inherit)
    # reporting.output_dir is implicitly resolved to base_dir/Report if not set, 
    # or we can set it explicitly to test the linkage.
    input_content = """
    name: "ExportDefaultApp"
    unified_root:
      name: ".ExportDefaultRoot"
    reporting:
      output_dir: "custom/reports"
    export:
      input_dir: null
    """
    
    def action(input_file):
        return loader.load(input_file, AppConfig)
        
    def validation(config):
        assert config.name == "ExportDefaultApp"
        # Verify reporting output is set as requested
        expected_report_dir = Path("custom/reports")
        assert Path(config.reporting.output_dir) == expected_report_dir
        
        # Verify export.input_dir inherited correctly: report_dir / "details"
        expected_input_dir = expected_report_dir / "details"
        # Compare as posix strings or Paths
        assert Path(config.export.input_dir) == expected_input_dir
        
        # Verify it uses forward slashes (serialization check handled by other tests, but good to know)

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="Export Defaults - Inheritance",
        description="Verify export.input_dir defaults to reporting.output_dir / 'details' when not specified.",
        input_filename="inherit_defaults.yaml",
        input_content=input_content,
        expected_output_desc="AppConfig with export.input_dir set to 'custom/reports/details'.",
        action=action,
        validation=validation
    )

def test_export_explicit_override(sandbox_root: Path):
    loader = FileConfigLoader()
    # Configuration with explicit export.input_dir (should NOT inherit)
    input_content = """
    name: "ExportOverrideApp"
    reporting:
      output_dir: "custom/reports"
    export:
      input_dir: "explicit/input"
    """
    
    def action(input_file):
        return loader.load(input_file, AppConfig)
        
    def validation(config):
        assert config.name == "ExportOverrideApp"
        
        # Verify explicit override is respected
        assert Path(config.export.input_dir) == Path("explicit/input")
        # Should NOT be related to reports dir
        assert Path(config.export.input_dir) != Path("custom/reports/details")

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="Export Defaults - Explicit Override",
        description="Verify user-provided export.input_dir overrides dynamic default.",
        input_filename="explicit_override.yaml",
        input_content=input_content,
        expected_output_desc="AppConfig with export.input_dir set to 'explicit/input'.",
        action=action,
        validation=validation
    )
