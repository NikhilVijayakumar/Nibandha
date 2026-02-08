
import pytest
from pathlib import Path
from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.configuration.infrastructure.file_loader import FileConfigLoader
from tests.sandbox.configuration.utils import run_config_test

# Tests for Phase 2: JSON Failures

def test_json_malformed(sandbox_root: Path):
    loader = FileConfigLoader()
    input_content = """
    {
        "name": "BrokenJson",
        "mode": "dev"
        "logging": {} 
    }
    """ # Missing comma after mode
    
    def action(input_file):
        # Should now succeed and return default config despite malformed input
        return loader.load(input_file, AppConfig)
            
    def validation(config):
        # Check for fallback
        assert isinstance(config, AppConfig)
        assert config.name == "Nibandha" # Default

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="JSON - Malformed Syntax (Fallback)",
        description="Verify fallback to default config when JSON syntax is invalid.",
        input_filename="malformed.json",
        input_content=input_content,
        expected_output_desc="Default AppConfig object (fallback)",
        action=action,
        validation=validation
    )

def test_json_wrong_root_type(sandbox_root: Path):
    loader = FileConfigLoader()
    # List instead of Dict
    input_content = """
    [
        {"name": "ListApp"}
    ]
    """
    
    def action(input_file):
        # Should now succeed by falling back to defaults (Robust Loading)
        return loader.load(input_file, AppConfig)
            
    def validation(config):
        # AppConfig created with defaults because input was a List (not a Dict)
        assert isinstance(config, AppConfig)
        # Name defaults to "Nibandha" (or pyproject name) because list input is ignored
        # config.name should be default
        assert config.mode == "production" # default

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="JSON - Wrong Root Type",
        description="Verify robust degradation when root element is an Array instead of an Object.",
        input_filename="list_root.json",
        input_content=input_content,
        expected_output_desc="AppConfig with default values (input ignored).",
        action=action,
        validation=validation
    )

def test_json_field_type_mismatch(sandbox_root: Path):
    loader = FileConfigLoader()
    # "logging" should be an object, but we give a string
    input_content = """
    {
        "name": "TypeMismatchApp",
        "logging": "enabled"
    }
    """
    
    def action(input_file):
        # Should succeed, ignoring the invalid "logging" field
        return loader.load(input_file, AppConfig)
            
    def validation(config):
        assert isinstance(config, AppConfig)
        assert config.name == "TypeMismatchApp" # Valid field retained
        # Logging field fell back to default because input "enabled" was invalid type
        assert config.logging.enabled is True # Default value
        # Verify it's a Proper LoggingConfig object
        assert config.logging.level == "INFO" # Default

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="JSON - Field Type Mismatch",
        description="Verify robust degradation when a field has an incorrect type.",
        input_filename="type_mismatch.json",
        input_content=input_content,
        expected_output_desc="AppConfig with valid fields retained and invalid ones defaulting.",
        action=action,
        validation=validation
    )
