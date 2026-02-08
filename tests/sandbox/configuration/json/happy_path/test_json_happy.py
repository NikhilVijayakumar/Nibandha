
import pytest
from pathlib import Path
from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.configuration.infrastructure.file_loader import FileConfigLoader
from tests.sandbox.configuration.utils import run_config_test

# Tests for Phase 1: JSON Happy Path

def test_json_empty_object(sandbox_root: Path):
    loader = FileConfigLoader()
    input_content = "{}"
    
    def action(input_file):
        return loader.load(input_file, AppConfig)
        
    def validation(config):
        assert isinstance(config, AppConfig)
        # Verify defaults
        assert config.name == "Nibandha" # Default fallback
        assert config.mode == "production"

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="JSON - Empty Object",
        description="Verify that an empty JSON object loads with default values.",
        input_filename="config.json",
        input_content=input_content,
        expected_output_desc="AppConfig with default values (name='Nibandha', mode='production')",
        action=action,
        validation=validation
    )

def test_json_single_module_logging(sandbox_root: Path):
    loader = FileConfigLoader()
    input_content = """
    {
        "logging": {
            "enabled": true,
            "level": "DEBUG"
        }
    }
    """
    
    def action(input_file):
        return loader.load(input_file, AppConfig)
        
    def validation(config):
        assert config.logging.enabled is True
        assert config.logging.level == "DEBUG"
        # Others should be default
        assert config.mode == "production"

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="JSON - Single Module (Logging)",
        description="Verify loading a configuration with only the logging module defined.",
        input_filename="logging_config.json",
        input_content=input_content,
        expected_output_desc="AppConfig with custom logging settings and default others.",
        action=action,
        validation=validation
    )

def test_json_full_config(sandbox_root: Path):
    loader = FileConfigLoader()
    # A robust full config matched to actual pydantic models
    input_content = """
    {
        "name": "FullApp",
        "mode": "dev",
        "logging": {
            "enabled": true,
            "level": "INFO"
        },
        "unified_root": {
            "name": ".MyRoot"
        },
        "reporting": {
            "project_name": "FullAppProject"
        },
        "export": {
            "style": "dark"
        }
    }
    """
    
    def action(input_file):
        return loader.load(input_file, AppConfig)
        
    def validation(config):
        assert config.name == "FullApp"
        assert config.mode == "dev"
        assert config.logging.enabled is True
        assert config.unified_root.name == ".MyRoot"
        assert config.reporting.project_name == "FullAppProject"
        assert config.export.style == "dark"
        # Check export formats if defined in input, or default
        # refined check based on input content which only had style


    run_config_test(
        sandbox_path=sandbox_root,
        test_name="JSON - Full Configuration",
        description="Verify loading a fully populated configuration object.",
        input_filename="full_config.json",
        input_content=input_content,
        expected_output_desc="AppConfig with all top-level sections populated.",
        action=action,
        validation=validation
    )

def test_json_unified_root_sync(sandbox_root: Path):
    loader = FileConfigLoader()
    # Provide app name but no unified_root name
    input_content = """
    {
        "name": "SyncApp"
    }
    """
    
    def action(input_file):
        return loader.load(input_file, AppConfig)
        
    def validation(config):
        assert config.name == "SyncApp"
        # Expect unified_root.name to be synced with AppConfig.name (prefixed with dot)
        assert config.unified_root.name == ".SyncApp"

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="JSON - Unified Root Sync",
        description="Verify unified_root.name defaults to AppConfig.name if not provided.",
        input_filename="sync_config.json",
        input_content=input_content,
        expected_output_desc="AppConfig with unified_root.name == '.SyncApp'",
        action=action,
        validation=validation
    )

def test_json_path_resolution(sandbox_root: Path):
    loader = FileConfigLoader()
    
    # CASE 1: Single App (Implicit) -> unified_root = .MyApp, App = MyApp
    input_single = """
    {
        "name": "MyApp"
    }
    """
    
    # CASE 2: Multi App -> unified_root = .System, App = OtherApp
    input_multi = """
    {
        "name": "OtherApp",
        "unified_root": {
            "name": ".System"
        }
    }
    """
    
    def action_single(input_file):
        return loader.load(input_file, AppConfig)

    def validation_single(config):
        # unified_root synced to .MyApp (because None provided)
        # Root matches App -> Single App Mode
        # Log dir should be .MyApp/logs
        # Output dir should be .MyApp/Report
        base = Path(".MyApp")
        assert config.unified_root.name == ".MyApp"
        # Paths should use forward slashes for cross-platform compatibility
        assert config.logging.log_dir == (base / "logs").as_posix()
        assert config.reporting.template_dir is not None
        assert config.reporting.template_dir.exists()
        assert config.reporting.template_dir.parts[-2:] == ("reporting", "templates")


    run_config_test(
        sandbox_path=sandbox_root,
        test_name="JSON - Path Resolution (Single App)",
        description="Verify path resolution when App Name matches Root (Single App).",
        input_filename="single_app_paths.json",
        input_content=input_single,
        expected_output_desc="Paths resolved directly under root.",
        action=action_single,
        validation=validation_single
    )

    def action_multi(input_file):
        return loader.load(input_file, AppConfig)
        
    def validation_multi(config):
        # Root (.System) != App (OtherApp) -> Multi App Mode
        # Log dir should be .System/OtherApp/logs
        # Output dir should be .System/OtherApp/Report
        base = Path(".System/OtherApp")
        assert config.unified_root.name == ".System"
        assert config.name == "OtherApp"
        # Paths should use forward slashes for cross-platform compatibility
        assert config.logging.log_dir == (base / "logs").as_posix()
        assert config.reporting.output_dir == base / "Report"


    run_config_test(
        sandbox_path=sandbox_root,
        test_name="JSON - Path Resolution (Multi App)",
        description="Verify path resolution when App Name differs from Root (Multi App).",
        input_filename="multi_app_paths.json",
        input_content=input_multi,
        expected_output_desc="Paths resolved under Root/AppName.",
        action=action_multi,
        validation=validation_multi
    )

def test_json_module_list(sandbox_root: Path):
    loader = FileConfigLoader()
    
    input_content = """
    {
        "name": "ModuleListApp",
        "reporting": {
            "module_discovery": ["Auth", "Core", "Utils"]
        }
    }
    """
    
    def action(input_file):
        return loader.load(input_file, AppConfig)
        
    def validation(config):
        assert isinstance(config, AppConfig)
        # Verify it loaded as a list
        assert config.reporting.module_discovery == ["Auth", "Core", "Utils"]

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="JSON - Module List Support",
        description="Verify module_discovery accepts a list of strings.",
        input_filename="module_list.json",
        input_content=input_content,
        expected_output_desc="AppConfig with list of modules in reporting config.",
        action=action,
        validation=validation
    )

def test_json_extra_fields_ignored(sandbox_root: Path):
    loader = FileConfigLoader()
    # Pydantic default is usually 'ignore' for extra fields unless configured otherwise
    input_content = """
    {
        "name": "ExtraFieldsApp",
        "unknown_field": "should_be_ignored",
        "nested": {
            "trash": "value"
        }
    }
    """
    
    def action(input_file):
        return loader.load(input_file, AppConfig)
        
    def validation(config):
        assert config.name == "ExtraFieldsApp"
        # Check that it didn't crash and loaded the known field
        # We don't check for unknown fields on the model as they are stripped

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="JSON - Extra Fields Ignored",
        description="Verify that unknown fields in the JSON are ignored (or allowed) without error.",
        input_filename="extra_fields.json",
        input_content=input_content,
        expected_output_desc="AppConfig loaded successfully, ignoring 'unknown_field'.",
        action=action,
        validation=validation
    )
