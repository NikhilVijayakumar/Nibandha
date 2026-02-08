
import pytest
from pathlib import Path
from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.configuration.infrastructure.file_loader import FileConfigLoader
from tests.sandbox.configuration.utils import run_config_test

def test_load_valid_yaml(sandbox_root: Path):
    loader = FileConfigLoader()
    
    input_content = """
    name: "YamlTestApp"
    mode: "dev"
    logging:
      enabled: true
      level: "DEBUG"
    """
    
    def action(input_file):
        return loader.load(input_file, AppConfig)
        
    def validation(config):
        assert isinstance(config, AppConfig)
        assert config.name == "YamlTestApp"
        assert config.mode == "dev"
        assert config.logging.level == "DEBUG"

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="Load Valid YAML",
        description="Verify loading a valid YAML configuration file.",
        input_filename="config.yaml",
        input_content=input_content,
        expected_output_desc="AppConfig object with name='YamlTestApp', mode='dev'",
        action=action,
        validation=validation
    )

def test_load_valid_json(sandbox_root: Path):
    loader = FileConfigLoader()
    
    input_content = """
    {
        "name": "JsonTestApp",
        "mode": "production",
        "unified_root": {
            "name": ".JsonRoot"
        }
    }
    """
    
    def action(input_file):
        return loader.load(input_file, AppConfig)
        
    def validation(config):
        assert isinstance(config, AppConfig)
        assert config.name == "JsonTestApp"
        assert config.mode == "production"
        assert config.unified_root.name == ".JsonRoot"

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="Load Valid JSON",
        description="Verify loading a valid JSON configuration file.",
        input_filename="config.json",
        input_content=input_content,
        expected_output_desc="AppConfig object with name='JsonTestApp'",
        action=action,
        validation=validation
    )

def test_load_invalid_format(sandbox_root: Path):
    loader = FileConfigLoader()
    
    input_content = "Just some text"
    
    def action(input_file):
        # Should now succeed and return default config
        return loader.load(input_file, AppConfig)
            
    def validation(config):
        assert isinstance(config, AppConfig)
        assert config.name == "Nibandha" # Default

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="Load Invalid Format (Fallback)",
        description="Verify fallback to default config when file has unsupported extension.",
        input_filename="config.txt", # Unsupported extension
        input_content=input_content,
        expected_output_desc="Default AppConfig object (fallback)",
        action=action,
        validation=validation
    )

def test_load_missing_file(sandbox_root: Path):
    loader = FileConfigLoader()
    
    def action(input_file):
        # We ignore the created input file and define a non-existent one
        missing_path = input_file.parent / "non_existent.yaml"
        # Should now succeed and return default config
        return loader.load(missing_path, AppConfig)
            
    def validation(config):
        # Check that we got a valid default AppConfig
        assert isinstance(config, AppConfig)
        assert config.name == "Nibandha" # Default name
        # We can't easily assert on stdout here without capsys, but the action succeeded
        # which means FileNotFoundError was caught.

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="Load Missing File (Fallback)",
        description="Verify fallback to default config when file is missing.",
        input_filename="placeholder.yaml",
        input_content="",
        expected_output_desc="Default AppConfig object (fallback)",
        action=action,
        validation=validation
    )

def test_load_validation_error(sandbox_root: Path):
    loader = FileConfigLoader()
    
    # Validation error: 'logging' should be a dict/object, but we provide a string
    input_content = """
    name: "BadConfigApp"
    logging: "This should be an object" 
    """
    
    def action(input_file):
        # Should succeed due to RobustConfigValidator
        return loader.load(input_file, AppConfig)
            
    def validation(config):
        assert isinstance(config, AppConfig)
        assert config.name == "BadConfigApp"
        # logging.level should be default ("INFO") because input was invalid
        assert config.logging.level == "INFO"

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="Load Validation Error (Robust)",
        description="Verify robust degradation when loading invalid types.",
        input_filename="bad_config.yaml",
        input_content=input_content,
        expected_output_desc="AppConfig with valid fields retained and defaults for invalid ones.",
        action=action,
        validation=validation
    )



def test_quality_target_sync(sandbox_root: Path):
    loader = FileConfigLoader()
    
    # Minimal config, should trigger sync logic
    input_content = '{"name": "SyncTargetApp"}'
    
    def action(input_file):
        return loader.load(input_file, AppConfig)
        
    def validation(config):
        # Assuming pyproject.toml defines package-dir as src/nikhil
        # If running in environment where pyproject.toml is present
        pyproject = Path.cwd() / "pyproject.toml"
        if pyproject.exists():
            # We expect sync to happen
            # Based on user input: package-dir = {"": "src/nikhil"}
            # So quality_target should be "src/nikhil"
            assert config.reporting.quality_target == "src/nikhil"
        else:
            pytest.skip("pyproject.toml not found in CWD")

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="Sync Quality Target",
        description="Verify reporting.quality_target syncs from pyproject.toml.",
        input_filename="sync_target.json",
        input_content=input_content,
        expected_output_desc="quality_target == src/nikhil",
        action=action,
        validation=validation
    )

def test_package_roots_sync(sandbox_root: Path):
    loader = FileConfigLoader()
    
    # Minimal config, should trigger package_roots sync
    input_content = '{"name": "SyncPackageApp"}'
    
    def action(input_file):
        return loader.load(input_file, AppConfig)
        
    def validation(config):
        # Assuming pyproject.toml defines name = "Nibandha"
        # package_roots should auto-populate to ["nibandha"]
        pyproject = Path.cwd() / "pyproject.toml"
        if pyproject.exists():
            # We expect sync to happen
            # Based on pyproject.toml: name = "Nibandha"
            # So package_roots should be ["nibandha"] (lowercased)
            assert config.reporting.package_roots == ["nibandha"]
        else:
            pytest.skip("pyproject.toml not found in CWD")

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="Sync Package Roots",
        description="Verify reporting.package_roots syncs from pyproject.toml project name.",
        input_filename="sync_package_roots.json",
        input_content=input_content,
        expected_output_desc="package_roots == ['nibandha']",
        action=action,
        validation=validation
    )

def test_config_portability(sandbox_root: Path):
    """Verify that default configuration does not contain absolute paths (portability)."""
    loader = FileConfigLoader()
    
    # Empty config to trigger defaults
    input_content = "{}"
    
    def action(input_file):
        return loader.load(input_file, AppConfig)
        
    def validation(config):
        # Check that template/style dirs are explicit relative paths (not None, not absolute)
        # Verify they match the expected relative defaults
        expected_tmpl = Path("src/nikhil/nibandha/reporting/templates")
        expected_exp_tmpl = Path("src/nikhil/nibandha/export/infrastructure/templates")
        expected_styles = Path("src/nikhil/nibandha/export/infrastructure/styles")
        
        assert config.reporting.template_dir == expected_tmpl, f"Reporting template_dir should be {expected_tmpl}"
        assert config.export.template_dir == expected_exp_tmpl, f"Export template_dir should be {expected_exp_tmpl}"
        assert config.export.styles_dir == expected_styles, f"Export styles_dir should be {expected_styles}"
        
        # Check that we can serialize it without error
        json_output = config.model_dump_json()
        assert "E:/" not in json_output, "Config should not contain absolute path 'E:/'"
        assert "src/nikhil/nibandha" in json_output, "Config should contain relative paths"

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="Config Portability",
        description="Verify defaults are portable explicit relative paths.",
        input_filename="portability.json",
        input_content=input_content,
        expected_output_desc="template_dir and styles_dir are relative paths",
        action=action,
        validation=validation
    )
