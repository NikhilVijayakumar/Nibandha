
import pytest
from pathlib import Path
from unittest.mock import patch
from nibandha.core import Nibandha, AppConfig, LogRotationConfig
from nibandha.core.rotation.infrastructure.manager import RotationManager
import logging

class TestCoreInitialization:
    """Core initialization logic, AppConfig, Defaults."""
    
    def test_app_config_defaults(self):
        """Test default values in AppConfig"""
        config = AppConfig(name="TestApp")
        assert config.name == "TestApp"
        assert config.log_level == "INFO"
        assert config.custom_folders == []

    @patch('builtins.input', side_effect=['n'])
    def test_creates_default_and_custom_folders(self, mock_input, temp_root, sample_app_config):
        """Test valid directory structure creation including custom folders"""
        config = AppConfig(name="CustomApp", custom_folders=["data", "cache"])
        nb = Nibandha(config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.bind() # Non-interactive by default now
        
        # Verify root
        assert nb.app_root.exists()
        assert nb.app_root.name == "CustomApp"
        
        # Verify standard folders
        assert (nb.app_root / "logs").exists()
        
        # Verify custom folders
        assert (nb.app_root / "data").exists()
        assert (nb.app_root / "cache").exists()

    def test_creates_rotation_folders_when_enabled(self, temp_root):
        """Test rotation-specific folder structure"""
        config = AppConfig(name="RotApp")
        nb = Nibandha(config, root_name=str(Path(temp_root) / ".Nibandha"))
        
        # Manually create enabled config
        nb.config_dir.mkdir(parents=True, exist_ok=True)
        rm = RotationManager(nb.config_dir, nb.app_root, logging.getLogger("test"))
        rot_config = LogRotationConfig(enabled=True)
        rm.save_config(rot_config)
        
        # Reload/Bind
        nb = Nibandha(config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.bind()
        
        assert (nb.app_root / "logs/data").exists()
        assert (nb.app_root / "logs/archive").exists()
