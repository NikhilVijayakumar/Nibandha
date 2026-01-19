
import pytest
from pathlib import Path
from unittest.mock import patch
from nibandha.core import Nibandha, LogRotationConfig
from nibandha.core.rotation.infrastructure.manager import RotationManager
import logging

class TestRotationCornerCases:
    """Edge cases, Legacy support, Disabled modes"""
    
    @patch('builtins.input', side_effect=['n'])
    def test_legacy_single_log_file(self, mock_input, temp_root, sample_app_config):
        """Test that legacy single log file works when rotation disabled"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        # Ensure disabled config
        nb.config_dir.mkdir(parents=True, exist_ok=True)
        rm = RotationManager(nb.config_dir, nb.app_root, logging.getLogger("test"))
        rm.save_config(LogRotationConfig(enabled=False))
        
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.bind()
        
        log_file = nb.app_root / "logs" / f"{sample_app_config.name}.log"
        assert log_file.exists()
        assert nb.current_log_file == log_file

    @patch('builtins.input', side_effect=['n'])
    def test_should_not_rotate_when_disabled(self, mock_input, temp_root, sample_app_config):
        """Test that rotation check returns False when disabled"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        # ensure disabled 
        nb.rotation_config = LogRotationConfig(enabled=False)
        nb.bind()
        
        assert nb.should_rotate() is False
        
    def test_no_config_returns_none(self, temp_root, sample_app_config):
        """Test that missing config returns None from manager load"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        rm = RotationManager(nb.config_dir, nb.app_root, logging.getLogger("test"))
        config = rm.load_config()
        assert config is None
