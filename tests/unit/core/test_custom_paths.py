
import pytest
from pathlib import Path
from nibandha.core.configuration.domain.config import AppConfig
from nibandha.core.bootstrap.application.app import Nibandha
from nibandha.core.rotation.domain.config import LogRotationConfig

def test_nibandha_paths_defaults(tmp_path):
    """Verify default paths without overrides."""
    config = AppConfig(name="MyApp")
    nb = Nibandha(config, root_name=str(tmp_path / ".Nibandha"))
    
    assert nb.config_dir == nb.root / "config"
    assert nb.report_dir == nb.app_root / "Report"
    assert nb._log_base == nb.app_root

def test_nibandha_paths_overrides(tmp_path):
    """Verify paths are overridden when provided in config."""
    custom_log = tmp_path / "custom_logs"
    custom_report = tmp_path / "custom_reports"
    custom_config = tmp_path / "custom_config"
    
    config = AppConfig(
        name="MyApp",
        log_dir=str(custom_log),
        report_dir=str(custom_report),
        config_dir=str(custom_config)
    )
    
    nb = Nibandha(config, root_name=str(tmp_path / ".Nibandha"))
    
    assert nb.config_dir == custom_config
    assert nb.report_dir == custom_report
    assert nb._log_base == custom_log

def test_bind_creates_custom_directories(tmp_path):
    """Verify bind() creates the overridden directories."""
    custom_log = tmp_path / "custom_logs"
    custom_config = tmp_path / "custom_config"
    
    config = AppConfig(
        name="MyApp",
        log_dir=str(custom_log),
        config_dir=str(custom_config)
    )
    
    nb = Nibandha(config, root_name=str(tmp_path / ".Nibandha"))
    # Disable rotation to test legacy path first
    nb.bind()
    
    assert custom_config.exists()
    assert (custom_log / "logs").exists() # Legacy creates "logs" inside log_base
    assert (custom_log / "logs" / "MyApp.log").exists()

def test_bind_creates_rotation_directories_in_custom_log_dir(tmp_path):
    """Verify rotation directories are created in custom log dir."""
    custom_log = tmp_path / "custom_logs"
    custom_config = tmp_path / "custom_config"
    
    config = AppConfig(
        name="MyApp",
        log_dir=str(custom_log),
        config_dir=str(custom_config)
    )
    
    nb = Nibandha(config, root_name=str(tmp_path / ".Nibandha"))
    nb.rotation_config = LogRotationConfig(enabled=True)
    # We need to save it or mocking? 
    # bind() attempts to load. If not found, it uses interactive/default.
    # To force enabled in test without interactive, we can pre-save it.
    
    # We need to manually set up the config file in the CUSTOM config dir
    custom_config.mkdir(parents=True, exist_ok=True)
    import yaml
    with open(custom_config / "rotation_config.yaml", "w") as f:
        yaml.dump(LogRotationConfig(enabled=True).dict(), f)
    
    nb.bind()
    
    # Verify paths
    assert (custom_log / "logs/data").exists()
    assert (custom_log / "logs/archive").exists()
    
    assert nb.current_log_file.parent == (custom_log / "logs/data")
