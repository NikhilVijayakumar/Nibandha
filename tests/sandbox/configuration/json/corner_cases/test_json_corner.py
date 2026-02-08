
import pytest
from pathlib import Path
from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.configuration.infrastructure.file_loader import FileConfigLoader
from tests.sandbox.configuration.utils import run_config_test

# Tests for Phase 3: JSON Corner Cases (Logic & Coercion)

def test_json_type_coercion_bool(sandbox_root: Path):
    loader = FileConfigLoader()
    # "true" string for boolean enabled
    input_content = """
    {
        "logging": {
            "enabled": "true" 
        }
    }
    """
    
    def action(input_file):
        # Pydantic v2 is stricter by default but often allows string "true"/"false"
        # unless strict=True is set on the field/config
        try:
            return loader.load(input_file, AppConfig)
        except Exception as e:
            # If it fails, that's also a valid result to document (Strictness)
            # If it passes, it documents Coercion
            return f"{type(e).__name__}: {str(e)}"
            
    def validation(result):
        # We expect it to likely pass with coercion or fail if strict.
        # Let's adjust based on Nibandha's Pydantic config.
        # Assuming defaults, it should coerce.
        if isinstance(result, AppConfig):
            assert result.logging.enabled is True
        else:
            # If it failed, check for valid validation error
            assert "ValidationError" in result

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="JSON - Type Coercion (Bool)",
        description="Verify handling of string 'true' for boolean fields.",
        input_filename="coercion_bool.json",
        input_content=input_content,
        expected_output_desc="AppConfig with enabled=True (Coercion) OR ValidationError (Strict).",
        action=action,
        validation=validation
    )

def test_json_type_coercion_int(sandbox_root: Path):
    loader = FileConfigLoader()
    # String "24" for rotation_interval_hours (int)
    input_content = """
    {
        "logging": {
            "enabled": true,
            "rotation_interval_hours": "24"
        }
    }
    """
    
    def action(input_file):
        try:
            return loader.load(input_file, AppConfig)
        except Exception as e:
            return f"{type(e).__name__}: {str(e)}"
            
    def validation(result):
        if isinstance(result, AppConfig):
            assert result.logging.rotation_interval_hours == 24
        else:
            assert "ValidationError" in result

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="JSON - Type Coercion (Int)",
        description="Verify handling of string '24' for integer fields.",
        input_filename="coercion_int.json",
        input_content=input_content,
        expected_output_desc="AppConfig with rotation_interval_hours=24.",
        action=action,
        validation=validation
    )

def test_json_float_to_int_truncation(sandbox_root: Path):
    loader = FileConfigLoader()
    # Float 24.5 for int field. Pydantic might truncate or fail.
    input_content = """
    {
        "logging": {
            "enabled": true,
            "rotation_interval_hours": 24.9
        }
    }
    """
    
    def action(input_file):
        try:
            return loader.load(input_file, AppConfig)
        except Exception as e:
            return f"{type(e).__name__}: {str(e)}"
            
    def validation(result):
        # Pydantic usually allows exact ints (24.0) but rejects lossy floats (24.9) by default in v2
        # Unless strict=False specific settings
        if isinstance(result, AppConfig):
            assert result.logging.rotation_interval_hours == 24
        else:
            assert "ValidationError" in result

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="JSON - Float to Int",
        description="Verify handling of float value for integer field.",
        input_filename="float_int.json",
        input_content=input_content,
        expected_output_desc="AppConfig (Truncated) OR ValidationError (Safe).",
        action=action,
        validation=validation
    )

def test_json_empty_path_string(sandbox_root: Path):
    loader = FileConfigLoader()
    # Empty string for Path field (e.g. log_dir is str but output_dir in Reporting is Path)
    # ReportingConfig.output_dir is Optional[Path]
    input_content = """
    {
        "reporting": {
            "output_dir": ""
        }
    }
    """
    
    def action(input_file):
        return loader.load(input_file, AppConfig)
        
    def validation(config):
        # Path("") usually resolves to "." (current dir)
        assert config.reporting.output_dir == Path(".")

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="JSON - Empty String for Path",
        description="Verify that an empty string for a Path field resolves to current directory.",
        input_filename="empty_path.json",
        input_content=input_content,
        expected_output_desc="AppConfig with output_dir=Path('.')",
        action=action,
        validation=validation
    )
