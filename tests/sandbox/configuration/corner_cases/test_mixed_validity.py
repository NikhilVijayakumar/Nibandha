
import pytest
from pathlib import Path
from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.configuration.infrastructure.file_loader import FileConfigLoader
from tests.sandbox.configuration.utils import run_config_test

def test_json_mixed_validity(sandbox_root: Path):
    loader = FileConfigLoader()
    
    # Mixed Validity JSON:
    # - "name": "MixedApp" (VALID)
    # - "logging": (VALID Dict structure)
    #    - "level": "DEBUG" (VALID)
    #    - "enabled": "not_a_bool" (INVALID Type - should fallback to default True)
    # - "export": "should_be_dict" (INVALID Type - should fallback to default ExportConfig)
    
    input_content = """
    {
        "name": "MixedApp",
        "logging": {
            "level": "DEBUG",
            "enabled": "not_a_bool" 
        },
        "export": "should_be_dict"
    }
    """
    
    def action(input_file):
        # We expect a valid AppConfig object, NOT a default one
        # It should contain the Valid fields, and defaults for Invalid ones.
        return loader.load(input_file, AppConfig)
        
    def validation(config):
        # 1. Valid Top-Level Field Retained
        assert config.name == "MixedApp", f"Expected 'MixedApp', got '{config.name}'"
        
        # 2. Valid Nested Field Retained
        assert config.logging.level == "DEBUG", "Expected logging.level='DEBUG' (Valid field retained)"
        
        # 3. Invalid Nested Field Defaulted (Partial Fallback)
        # "enabled" was invalid string, should fall back to default True
        assert config.logging.enabled is True, "Expected logging.enabled=True (Default fallback)"
        
        # 4. Invalid Section Defaulted (Full Section Fallback)
        # "export" was invalid type (str), should default to factory ExportConfig
        # Check a default value
        assert config.export.style == "default" # Default style

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="JSON - Mixed Validity (Partial Fallback)",
        description="Verify system keeps valid fields (Top & Nested) while defaulting invalid ones.",
        input_filename="mixed_validity.json",
        input_content=input_content,
        expected_output_desc="AppConfig with mixed valid values and defaults.",
        action=action,
        validation=validation
    )

def test_yaml_recursive_recovery(sandbox_root: Path):
    loader = FileConfigLoader()
    
    # YAML with deep validation issues
    # - reporting (VALID)
    #   - project_name: "YamlProject" (VALID)
    #   - doc_paths: (INVALID - List instead of Dict) -> defaults
    
    input_content = """
    reporting:
      project_name: "YamlProject"
      doc_paths:
        - "should"
        - "be"
        - "map"
    """
    
    def action(input_file):
        return loader.load(input_file, AppConfig)
        
    def validation(config):
        # Valid property retained
        assert config.reporting.project_name == "YamlProject"
        
        # Invalid property defaults
        # doc_paths default is {"functional": ..., "technical": ...}
        assert "functional" in config.reporting.doc_paths
        assert isinstance(config.reporting.doc_paths, dict)

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="YAML - Recursive Recovery",
        description="Verify recovery from invalid type in nested structure (List vs Dict).",
        input_filename="recursive.yaml",
        input_content=input_content,
        expected_output_desc="AppConfig with defaults for invalid nested structure.",
        action=action,
        validation=validation
    )

def test_dict_partial_validity(sandbox_root: Path):
    # Testing Dictionary loading specifically via FileConfigLoader (which supports it via robust validator internally if mapped)
    # Actually FileConfigLoader expects JSON/YAML file. 
    # But we can verify "Dictionary-like" behavior via python file loading logic 
    # similar to test_dict_parity.py
    
    from nibandha.configuration.application.configuration_manager import ConfigurationManager
    
    # Input data as Python Dict
    input_data = {
        "mode": "dev",         # Valid
        "logging": 12345,      # Invalid Type (Int vs Dict) -> Default
        "unified_root": {
            "name": ".DictRoot" # Valid
        }
    }
    
    def action(input_file):
        # Direct ConfigManager call to test Dict path
        return ConfigurationManager.load_from_dict(input_data)
        
    def validation(config):
        assert config.mode == "dev"
        assert config.unified_root.name == ".DictRoot"
        # Logging should be default because 12345 is invalid
        assert config.logging.level == "INFO"
        assert config.logging.enabled is True

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="Dict - Mixed Validity",
        description="Verify ConfigurationManager.load_from_dict handles mixed valid/invalid data.",
        input_filename="dict_mixed.py", # Pseudo filename for report
        input_content=str(input_data),
        expected_output_desc="AppConfig with valid dict fields retained.",
        action=action,
        validation=validation
    )
