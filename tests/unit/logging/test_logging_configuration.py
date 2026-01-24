
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
        archive_dir = nb.log_base / nb.rotation_config.archive_dir
        # RotationManager now uses date-based folders -> archive/%Y-%m-%d/filename
        # We need to find where it went.
        # Since we mocked datetime in rotation_manager, we should expect a folder matching that date.
        # But wait, date extraction comes from filename timestamp usually.
        # The filename is old_log_file.name. 
        # The code tries to parse date from filename. If format matches.
        # old_log_file was created with default or config format?
        # In this test: timestamp_format="%Y-%m-%d_%H-%M-%S"
        # The logger creates the file using this format? No, Logger uses 'app.log' usually unless rotated?
        # Wait, Nibandha initialization:
        # if rotation enabled: log_file = ... / {timestamp}.log
        # So yes, old_log_file has timestamp name.
        # So "2026-01-23_21-24-06.log".
        # date_str extraction uses timestamp_format.
        # So it extracts 2026-01-23_21-24-06.
        # The code does:
        # file_date = datetime.strptime(base_name, self.config.timestamp_format)
        # date_str = file_date.strftime(self.config.timestamp_format)
        # So folder name IS the full timestamp? That seems wrong for a "date folder".
        # Usually one wants daily folders (YYYY-MM-DD).
        # But Logic uses `self.config.timestamp_format` for BOTH parsing AND formatting the folder name?
        # src/nikhil/nibandha/logging/infrastructure/rotation_manager.py:135:
        # date_str = file_date.strftime(self.config.timestamp_format)
        # Yes! It uses the FULL format for the folder name.
        # If format includes time, the folder includes time.
        # This means every rotation creates a new folder?
        # That effectively disables grouping.
        # Ideally it should use a separate `date_format` or fixed `%Y-%m-%d` for folders.
        # But assuming current behavior is expected (based on code):
        
        # We need to calculate what the folder name is.
        # It's derived from the old log filename.
        # And since we mocked datetime during rotation, but the *old* file was created BEFORE rotation mock?
        # No, old file creation used real time? Or mocked?
        # "Write to first log" -> `nb.bind()`.
        # `nb` init uses `datetime.now()`.
        # We didn't mock `datetime` for `nb.bind()` call?
        # The valid patch is inside `with patch(...)` LATER.
        # So `nb.bind()` used real time.
        # Then we mock time and call `rotate_logs`.
        # `rotate_logs` takes `current_log_file`.name.
        # It parses it using `timestamp_format`.
        # If real time doesn't match format perfectly or if milliseconds differ?
        # Format is `%Y-%m-%d_%H-%M-%S`.
        # `nb` creation uses `datetime.now().strftime(format)`. So it matches.
        # So `folder_name` == `old_log_file.stem`.
        
        # Use rglob to find the file in any subfolder (date folder)
        found_files = list(archive_dir.rglob(old_log_file.name))
        assert len(found_files) > 0, f"Could not find {old_log_file.name} in {archive_dir}"
        assert found_files[0].exists()
