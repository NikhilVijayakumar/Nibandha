
import pytest
import logging
from pathlib import Path
from unittest.mock import patch
from nibandha import Nibandha
from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.configuration.domain.models.rotation_config import LogRotationConfig
from nibandha.logging.infrastructure.rotation_manager import RotationManager
import sys

class TestLoggingConfiguration:
    """Scenarios: Test different configurations and complex setups."""

    @patch('builtins.input', side_effect=['n'])
    def test_daily_timestamp_format_default(self, mock_input, temp_root, sample_app_config):
        """Test that default timestamp format is daily"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.rotation_config = LogRotationConfig(enabled=True)
        
        # Verify default timestamp format is daily
        assert nb.rotation_config.timestamp_format == "%Y-%m-%d"
        
    @patch('nibandha.unified_root.bootstrap.datetime')
    @patch('nibandha.logging.infrastructure.rotation_manager.datetime')
    def test_daily_log_consolidation(self, mock_rm_dt, mock_boot_dt, temp_root, sample_app_config):
        """Test that logs consolidate into same daily file on restart"""
        from datetime import datetime
        
        # Setup mocks
        mock_now = datetime(2026, 1, 15, 12, 0, 0)
        
        # Sync both mocks
        mock_rm_dt.now.return_value = mock_now
        mock_rm_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        mock_rm_dt.strptime = datetime.strptime
        mock_rm_dt.fromtimestamp = datetime.fromtimestamp
        
        mock_boot_dt.now.return_value = mock_now
        mock_boot_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        mock_boot_dt.strptime = datetime.strptime
        mock_boot_dt.fromtimestamp = datetime.fromtimestamp
        
        # Initialize
        config = AppConfig(name="TestApp", log_level="INFO")
        nb1 = Nibandha(config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb1.config_dir.mkdir(parents=True, exist_ok=True)
        rm = RotationManager(nb1.config_dir, nb1.app_root, logging.getLogger("test"))
        rm.save_config(LogRotationConfig(enabled=True))
        
        # First Run
        nb1.bind()
        nb1.logger.info("First run message")
        
        # Clean handlers to release file lock
        for handler in nb1.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()
                handler.close()
        
        first_log_file = nb1.current_log_file
        # Assert filename matches MOCKED date
        assert first_log_file.name == "2026-01-15.log"
        
        # Second Run (Simulate restart later same day)
        mock_now2 = datetime(2026, 1, 15, 14, 0, 0)
        mock_rm_dt.now.return_value = mock_now2
        mock_boot_dt.now.return_value = mock_now2
        
        nb2 = Nibandha(config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb2.bind()
        nb2.logger.info("Second run message")
        
        second_log_file = nb2.current_log_file
        assert second_log_file.name == "2026-01-15.log"
        
        # Verify content
        content = second_log_file.read_text()
        assert "First run message" in content
        assert "Second run message" in content

    @patch('builtins.input', side_effect=['n'])
    def test_rotation_with_file_handler_attachment(self, mock_input, temp_root, sample_app_config):
        """Test that log rotation still works with new handler attachment"""
        import time
        
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.config_dir.mkdir(parents=True, exist_ok=True)
        rm = RotationManager(nb.config_dir, nb.app_root, logging.getLogger("test"))
        rm.save_config(LogRotationConfig(enabled=True, timestamp_format="%Y-%m-%d_%H-%M-%S"))
        
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.bind()
        
        # Write to first log
        nb.logger.info("Before rotation")
        for handler in nb.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()
        
        old_log_file = nb.current_log_file
        old_content = old_log_file.read_text()
        assert "Before rotation" in old_content
        
        from datetime import datetime, timedelta
        
        # Mock datetime to ensure rotation creates new timestamp
        # Patch where RotationManager imports datetime
        with patch('nibandha.logging.infrastructure.rotation_manager.datetime') as mock_dt:
             base_time = datetime.now() + timedelta(seconds=10)
             mock_dt.now.side_effect = [base_time, base_time + timedelta(seconds=2)]
             mock_dt.fromtimestamp = datetime.fromtimestamp
             
             nb.rotate_logs()
        
        # Write to new log
        nb.logger.info("After rotation")
        for handler in nb.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()
        
        # Verify new log has new content
        new_log_file = nb.current_log_file
        assert new_log_file != old_log_file
        assert new_log_file.exists()
        
        new_content = new_log_file.read_text()
        assert "After rotation" in new_content
        assert "Before rotation" not in new_content
        
        # Verify old log moved to archive
        archive_dir = nb.app_root / nb.rotation_config.archive_dir
        assert (archive_dir / old_log_file.name).exists()
