
import pytest
import json
from pathlib import Path
from nibandha.configuration.domain.models.app_config import AppConfig
from tests.sandbox.configuration.utils import run_config_test

# Tests for Phase 5: Format Parity - Dictionary (Direct Model Validation)

import importlib.util

def load_dict_from_file(file_path: Path) -> dict:
    """Helper to dynamically load a dictionary from a python file."""
    spec = importlib.util.spec_from_file_location("input_module", file_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.config_data
    return {}

def test_dict_full_config(sandbox_root: Path):
    # Direct dictionary input
    input_data = {
        "name": "FullAppDict",
        "mode": "dev",
        "logging": {
            "enabled": True,
            "level": "INFO"
        },
        "unified_root": {
            "name": ".MyRootDict"
        },
        "reporting": {
            "project_name": "FullAppProjectDict"
        },
        "export": {
            "style": "dark"
        }
    }
    
    # We display valid Python dictionary syntax in the report
    # Use repr to ensure True/False are Python-compatible, not JSON lowercase true/false
    input_content = f"config_data = {repr(input_data)}"
    
    def action(input_file):
        # Use ConfigurationManager which now handles validation internally
        from nibandha.configuration.application.configuration_manager import ConfigurationManager
        loaded_data = load_dict_from_file(input_file)
        return ConfigurationManager.load_from_dict(loaded_data)
        
    def validation(config):
        assert config.name == "FullAppDict"
        assert config.mode == "dev"
        assert config.logging.enabled is True
        assert config.logging.level == "INFO"
        assert config.unified_root.name == ".MyRootDict"
        assert config.reporting.project_name == "FullAppProjectDict"
        assert config.export.style == "dark"

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="Dict - Full Configuration",
        description="Verify initializing AppConfig from a Python dictionary using ConfigurationManager.",
        input_filename="config_data.py", 
        input_content=input_content,
        expected_output_desc="AppConfig with all top-level sections populated.",
        action=action,
        validation=validation
    )

def test_dict_type_mismatch(sandbox_root: Path):
    # Invalid dict structure
    input_data = {
        "name": "TypeMismatchDict",
        "logging": "enabled" # Should be dict
    }
    
    # We display valid Python dictionary syntax in the report
    input_content = f"config_data = {repr(input_data)}"
    
    def action(input_file):
        # ConfigurationManager should now handle this robustly and catch any remaining errors
        from nibandha.configuration.application.configuration_manager import ConfigurationManager
        loaded_data = load_dict_from_file(input_file)
        return ConfigurationManager.load_from_dict(loaded_data)
            
    def validation(config):
        # Should succeed (Robust Validator fixes it, or Fallback kicks in)
        assert isinstance(config, AppConfig)
        assert config.name == "TypeMismatchDict"
        # logging should be default because "enabled" string was rejected
        assert config.logging.enabled is True

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="Dict - Type Mismatch (Resilient)",
        description="Verify robust degradation when initializing AppConfig from invalid dictionary.",
        input_filename="invalid_data.py",
        input_content=input_content,
        expected_output_desc="AppConfig with valid fields retained and defaults for invalid ones.",
        action=action,
        validation=validation
    )
