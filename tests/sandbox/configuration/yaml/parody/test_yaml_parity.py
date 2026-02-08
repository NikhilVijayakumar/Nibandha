
import pytest
from pathlib import Path
from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.configuration.infrastructure.file_loader import FileConfigLoader
from tests.sandbox.configuration.utils import run_config_test

# Tests for Phase 4: Format Parity - YAML

def test_yaml_full_config(sandbox_root: Path):
    loader = FileConfigLoader()
    # Replicating test_json_full_config in YAML
    input_content = """
    name: "FullAppYaml"
    mode: "dev"
    logging:
      enabled: true
      level: "INFO"
    unified_root:
      name: ".MyRootYaml"
    reporting:
      project_name: "FullAppProjectYaml"
    export:
      style: "dark"
    """
    
    def action(input_file):
        return loader.load(input_file, AppConfig)
        
    def validation(config):
        assert config.name == "FullAppYaml"
        assert config.mode == "dev"
        assert config.logging.enabled is True
        assert config.logging.level == "INFO"
        assert config.unified_root.name == ".MyRootYaml"
        assert config.reporting.project_name == "FullAppProjectYaml"
        assert config.export.style == "dark"

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="YAML - Full Configuration",
        description="Verify loading a fully populated YAML configuration matches JSON behavior.",
        input_filename="full_config.yaml",
        input_content=input_content,
        expected_output_desc="AppConfig with all top-level sections populated (YAML source).",
        action=action,
        validation=validation
    )

def test_yaml_malformed(sandbox_root: Path):
    loader = FileConfigLoader()
    # Invalid YAML syntax (mapping values not allowed here)
    input_content = """
    name: "BrokenYaml"
    : invalid_key_start
    """ 
    
    def action(input_file):
        # Should now succeed and return default config despite malformed input
        return loader.load(input_file, AppConfig)
            
    def validation(config):
        # Check for fallback
        assert isinstance(config, AppConfig)
        assert config.name == "Nibandha" # Default

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="YAML - Malformed Syntax (Fallback)",
        description="Verify fallback to default config when YAML syntax is invalid.",
        input_filename="malformed.yaml",
        input_content=input_content,
        expected_output_desc="Default AppConfig object (fallback)",
        action=action,
        validation=validation
    )
