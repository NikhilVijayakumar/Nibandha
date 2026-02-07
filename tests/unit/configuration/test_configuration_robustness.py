
import pytest
from pathlib import Path
from pydantic import BaseModel
from unittest.mock import MagicMock, patch, ANY

from nibandha.configuration.infrastructure.file_loader import FileConfigLoader
from nibandha.unified_root.bootstrap import Nibandha
from nibandha.configuration.domain.models.app_config import AppConfig

# --- Models ---
class MockConfig(BaseModel):
    name: str

# --- FileConfigLoader Tests ---

def test_loader_file_not_found(tmp_path):
    loader = FileConfigLoader()
    with pytest.raises(FileNotFoundError):
        loader.load(tmp_path / "missing.yaml", MockConfig)

def test_loader_unsupported_extension_load(tmp_path):
    f = tmp_path / "config.txt"
    f.touch()
    loader = FileConfigLoader()
    with pytest.raises(ValueError, match="Unsupported"):
        loader.load(f, MockConfig)

def test_loader_unsupported_extension_save(tmp_path):
    loader = FileConfigLoader()
    with pytest.raises(ValueError, match="Unsupported"):
        loader.save(tmp_path / "config.txt", MockConfig(name="test"))

def test_loader_save_load_json(tmp_path):
    loader = FileConfigLoader()
    p = tmp_path / "config.json"
    
    cfg = MockConfig(name="json_test")
    loader.save(p, cfg)
    
    loaded = loader.load(p, MockConfig)
    assert loaded.name == "json_test"

def test_loader_save_load_yaml(tmp_path):
    loader = FileConfigLoader()
    p = tmp_path / "config.yaml"
    
    cfg = MockConfig(name="yaml_test")
    loader.save(p, cfg)
    
    loaded = loader.load(p, MockConfig)
    assert loaded.name == "yaml_test"

def test_loader_malformed_json(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("{bad", encoding="utf-8")
    loader = FileConfigLoader()
    with pytest.raises(Exception): # json.JSONDecodeError
        loader.load(p, MockConfig)

# --- Bootstrap Tests ---

@pytest.fixture
def app_config():
    return AppConfig(name="TestApp", log_level="DEBUG", config_dir="conf")

def test_bootstrap_interactive_setup(tmp_path, app_config):
    # Mock input to return yes and config values (handled by prompt_and_cache_config mock generally, but here we integration test logic via bootstrap)
    
    # We want to hit bootstrap.py line 96: if interactive_setup:
    # Requires rotation_config to be None initially (so load_config fails or returns None)
    
    # Mock RotationManager to return None on load_config
    # And return valid config on prompt
    
    # Updated patch path to where RotationManager is actually used (LoggingCoordinator)
    with patch("nibandha.logging.application.logging_coordinator.RotationManager") as MockRM:
        instance = MockRM.return_value
        instance.load_config.return_value = None
        
        # When prompt called, return a config
        from nibandha.configuration.domain.models.rotation_config import LogRotationConfig
        mock_rc = LogRotationConfig(enabled=True)
        instance.prompt_and_cache_config.return_value = mock_rc
        
        # Instantiate Nibandha
        root = Nibandha(app_config, root_name=str(tmp_path))
        
        # Call bind with interactive=True
        # Need to mock setup_logger to avoid real file issues?
        with patch("nibandha.logging.application.logging_coordinator.setup_logger"):
            root.bind(interactive_setup=True)
        
        # Verify prompt called
        instance.prompt_and_cache_config.assert_called_once()
        assert root.rotation_config == mock_rc

def test_bootstrap_default_setup_no_rot(tmp_path, app_config):
    # Case where load fails/None, interactive=False -> enabled=False
    with patch("nibandha.logging.application.logging_coordinator.RotationManager") as MockRM:
        instance = MockRM.return_value
        instance.load_config.return_value = None
        
        root = Nibandha(app_config, root_name=str(tmp_path))
        
        with patch("nibandha.logging.application.logging_coordinator.setup_logger"):
            root.bind(interactive_setup=False)
            
        instance.save_config.assert_called()
        assert root.rotation_config.enabled == False

def test_bootstrap_properties_without_bind(app_config):
    n = Nibandha(app_config, root_name="root")
    # Verify properties don't crash when context is None
    assert n.root == Path("root")
    assert n.app_root == Path("root") / "TestApp"
    # assert n.config_dir... (Needs mock or logic check)

def test_passthrough_methods(app_config):
    # Test should_rotate, rotate_logs, cleanup passthroughs
    n = Nibandha(app_config)
    n.rotation_manager = MagicMock()
    
    n.should_rotate()
    n.rotation_manager.should_rotate.assert_called()
    
    n.rotate_logs()
    n.rotation_manager.rotate_logs.assert_called()
    
    n.cleanup_old_archives()
    n.rotation_manager.cleanup_old_archives.assert_called()
    
    # Test safe None
    n.rotation_manager = None
    assert n.should_rotate() == False
    assert n.cleanup_old_archives() == 0
    n.rotate_logs() # Should not crash
