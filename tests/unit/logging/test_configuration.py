
import pytest
import logging
from pathlib import Path
from unittest.mock import patch
from nibandha.core import Nibandha, AppConfig, LogRotationConfig
from nibandha.core.rotation.infrastructure.manager import RotationManager
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
        
    @patch('builtins.input', side_effect=['n'])
    def test_daily_log_consolidation(self, mock_input, temp_root, sample_app_config):
        """Test that logs consolidate into same daily file on restart"""
        from datetime import datetime
        from unittest.mock import patch as mock_patch
        
        # Mock datetime to ensure same day
        fixed_date = datetime(2026, 1, 15, 10, 30, 15)
        first_log_file = None # Init outer scope
        
        # Patch datetime where usage occurs
        # Nibandha bind uses datetime.now() calling app.py imports
        # So we patch 'nibandha.core.bootstrap.application.app.datetime'
        
        with mock_patch('nibandha.core.bootstrap.application.app.datetime') as mock_datetime:
            mock_datetime.now.return_value = fixed_date
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            # First initialization
            # First initialization
            nb1 = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
            nb1.config_dir.mkdir(parents=True, exist_ok=True)
            rm = RotationManager(nb1.config_dir, nb1.app_root, logging.getLogger("test"))
            rm.save_config(LogRotationConfig(enabled=True))
            
            nb1 = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
            nb1.bind()
            nb1.logger.info("First run message")
            
            # Force flush
            for handler in nb1.logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    handler.flush()
                    handler.close()
            
            first_log_file = nb1.current_log_file
            assert first_log_file.name == "2026-01-15.log"
        
        # Simulate restart (different time, same day)
        fixed_date2 = datetime(2026, 1, 15, 14, 45, 32)
        
        with mock_patch('nibandha.core.bootstrap.application.app.datetime') as mock_datetime:
            mock_datetime.now.return_value = fixed_date2
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            # Second initialization - should use SAME file
            nb2 = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
            nb2.bind()
            nb2.logger.info("Second run message")
            
            # Force flush
            for handler in nb2.logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    handler.flush()
            
            second_log_file = nb2.current_log_file
            
            # Should be the SAME file (same filename)
            assert second_log_file.name == "2026-01-15.log"
            assert second_log_file == first_log_file
            
            # Verify both messages in same file
            content = second_log_file.read_text()
            assert "First run message" in content
            assert "Second run message" in content
            
            # Verify only ONE log file exists in data directory
            data_dir = nb2.app_root / "logs/data"
            log_files = list(data_dir.glob("*.log"))
            assert len(log_files) == 1

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
        with patch('nibandha.core.rotation.infrastructure.manager.datetime') as mock_dt:
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
