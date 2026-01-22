
import pytest
import logging
from pathlib import Path
from unittest.mock import patch
from nibandha import Nibandha
from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.configuration.domain.models.rotation_config import LogRotationConfig
from nibandha.logging.infrastructure.rotation_manager import RotationManager

class TestLoggingInitialization:
    """Happy Path: Test handler initialization and basic logging flow."""
    
    @patch('builtins.input', side_effect=['n'])
    def test_handler_attachment_to_named_logger(self, mock_input, temp_root, sample_app_config):
        """Test that handlers are attached to named logger, not ROOT"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.config_dir.mkdir(parents=True, exist_ok=True)
        rm = RotationManager(nb.config_dir, nb.app_root, logging.getLogger("test"))
        rm.save_config(LogRotationConfig(enabled=False))
        
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.bind()
        
        # Verify handlers are attached to named logger
        assert len(nb.logger.handlers) >= 2  # FileHandler + StreamHandler
        assert any(isinstance(h, logging.FileHandler) for h in nb.logger.handlers)
        assert any(isinstance(h, logging.StreamHandler) for h in nb.logger.handlers)
        
        # Verify propagate is False to prevent duplicate logs
        assert nb.logger.propagate is False
        
    @patch('builtins.input', side_effect=['n'])
    def test_log_file_is_not_empty(self, mock_input, temp_root, sample_app_config):
        """Test that log files are actually written to"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.config_dir.mkdir(parents=True, exist_ok=True)
        rm = RotationManager(nb.config_dir, nb.app_root, logging.getLogger("test"))
        rm.save_config(LogRotationConfig(enabled=False))
        
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.bind()
        
        # Write test messages
        nb.logger.info("Test message 1")
        nb.logger.warning("Test message 2")
        nb.logger.error("Test message 3")
        
        # Force flush handlers
        for handler in nb.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()
        
        # Verify log file exists and is NOT empty
        log_file = nb.app_root / "logs" / f"{sample_app_config.name}.log"
        assert log_file.exists()
        assert log_file.stat().st_size > 0
        
        # Verify content
        content = log_file.read_text()
        assert "Test message 1" in content
        assert "Test message 2" in content
        assert "Test message 3" in content

    @patch('builtins.input', side_effect=['n'])
    def test_child_logger_writes_to_file(self, mock_input, temp_root, sample_app_config):
        """Test that child loggers also write to file"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.config_dir.mkdir(parents=True, exist_ok=True)
        rm = RotationManager(nb.config_dir, nb.app_root, logging.getLogger("test"))
        rm.save_config(LogRotationConfig(enabled=False))
        
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.bind()
        
        # Create child logger
        child_logger = logging.getLogger(f"{sample_app_config.name}.module.submodule")
        child_logger.info("Message from child logger")
        
        # Also log from parent
        nb.logger.info("Message from parent logger")
        
        # Force flush
        for handler in nb.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()
        
        # Verify both messages in log file
        log_file = nb.app_root / "logs" / f"{sample_app_config.name}.log"
        content = log_file.read_text()
        assert "Message from child logger" in content
        assert "Message from parent logger" in content
