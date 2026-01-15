import pytest
import logging
from pathlib import Path
from unittest.mock import patch
from nibandha.core import Nibandha, AppConfig, LogRotationConfig


class TestBugFixes:
    """Test bug fixes for handler attachment and timestamp format"""
    
    @patch('builtins.input', side_effect=['n'])
    def test_handler_attachment_to_named_logger(self, mock_input, temp_root, sample_app_config):
        """Test that handlers are attached to named logger, not ROOT (Bug #1 fix)"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.rotation_config = LogRotationConfig(enabled=False)
        nb._save_rotation_config(nb.rotation_config)
        
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.bind()
        
        # Verify handlers are attached to named logger
        assert len(nb.logger.handlers) >= 2  # FileHandler + StreamHandler
        assert any(isinstance(h, logging.FileHandler) for h in nb.logger.handlers)
        assert any(isinstance(h, logging.StreamHandler) for h in nb.logger.handlers)
        
        # Verify propagate is False to prevent duplicate logs
        assert nb.logger.propagate is False
        
        # Verify ROOT logger doesn't have our handlers
        root_logger = logging.getLogger()
        # Root may have handlers, but our specific handlers should be on named logger only
        
    @patch('builtins.input', side_effect=['n'])
    def test_log_file_is_not_empty(self, mock_input, temp_root, sample_app_config):
        """Test that log files are actually written to (Bug #1 fix verification)"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.rotation_config = LogRotationConfig(enabled=False)
        nb._save_rotation_config(nb.rotation_config)
        
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
        assert log_file.stat().st_size > 0, "Log file should not be empty!"
        
        # Verify content
        content = log_file.read_text()
        assert "Test message 1" in content
        assert "Test message 2" in content
        assert "Test message 3" in content
    
    @patch('builtins.input', side_effect=['n'])
    def test_child_logger_writes_to_file(self, mock_input, temp_root, sample_app_config):
        """Test that child loggers also write to file (Bug #1 fix verification)"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.rotation_config = LogRotationConfig(enabled=False)
        nb._save_rotation_config(nb.rotation_config)
        
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
    
    @patch('builtins.input', side_effect=['n'])
    def test_daily_timestamp_format_default(self, mock_input, temp_root, sample_app_config):
        """Test that default timestamp format is daily (Bug #2 fix)"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.rotation_config = LogRotationConfig(enabled=True)
        
        # Verify default timestamp format is daily
        assert nb.rotation_config.timestamp_format == "%Y-%m-%d"
        
    @patch('builtins.input', side_effect=['n'])
    def test_daily_log_consolidation(self, mock_input, temp_root, sample_app_config):
        """Test that logs consolidate into same daily file on restart (Bug #2 fix verification)"""
        from datetime import datetime
        from unittest.mock import patch as mock_patch
        
        # Mock datetime to ensure same day
        fixed_date = datetime(2026, 1, 15, 10, 30, 15)
        
        with mock_patch('nibandha.core.datetime') as mock_datetime:
            mock_datetime.now.return_value = fixed_date
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            # First initialization
            nb1 = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
            nb1.rotation_config = LogRotationConfig(enabled=True)
            nb1._save_rotation_config(nb1.rotation_config)
            
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
        
        with mock_patch('nibandha.core.datetime') as mock_datetime:
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
            assert len(log_files) == 1, f"Expected 1 log file, found {len(log_files)}"
    
    @patch('builtins.input', side_effect=['n'])
    def test_rotation_with_file_handler_attachment(self, mock_input, temp_root, sample_app_config):
        """Test that log rotation still works with new handler attachment"""
        import time
        
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.rotation_config = LogRotationConfig(enabled=True)
        nb._save_rotation_config(nb.rotation_config)
        
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
        
        # Rotate
        time.sleep(0.1)
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
        assert "Before rotation" not in new_content  # Old message should be in archive
        
        # Verify old log moved to archive
        archive_dir = nb.app_root / nb.rotation_config.archive_dir
        assert (archive_dir / old_log_file.name).exists()
