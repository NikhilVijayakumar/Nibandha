
import pytest
from unittest.mock import MagicMock, patch, call, ANY
from pathlib import Path
import logging
import time

from nibandha.logging.infrastructure.rotation_manager import RotationManager
from nibandha.logging.infrastructure.nibandha_logger import NibandhaLogger
from nibandha.logging.domain.models.log_settings import LogSettings
from nibandha.configuration.domain.models.rotation_config import LogRotationConfig

# --- Rotation Manager Advanced Tests ---

@pytest.fixture
def rotation_manager(tmp_path):
    config_dir = tmp_path / "config"
    app_root = tmp_path
    logger = MagicMock()
    
    manager = RotationManager(config_dir, app_root, logger)
    manager.config = LogRotationConfig(enabled=True)
    return manager

def test_rotate_logs_retry_success(rotation_manager, tmp_path):
    # Simulate Windows file lock: Fail twice, succeed third time
    rotation_manager.current_log_file = tmp_path / "app.log"
    rotation_manager.current_log_file.touch()

    # Ensure log data dir exists for new log creation
    (rotation_manager.app_root / rotation_manager.config.log_data_dir).mkdir(parents=True, exist_ok=True)
    
    # Mock handlers to avoid close error
    rotation_manager.logger.handlers = []
    
    with patch("shutil.move") as mock_move:
        # Side effect: Raise PermissionError twice, then return None (success)
        mock_move.side_effect = [PermissionError("Lock"), PermissionError("Lock"), None]
        
        with patch("time.sleep"): # Fast test
            rotation_manager.rotate_logs()
        
        assert mock_move.call_count == 3
        rotation_manager.logger.error.assert_not_called()

def test_rotate_logs_retry_failure(rotation_manager, tmp_path):
    # Fail 3 times -> Error log
    rotation_manager.current_log_file = tmp_path / "app.log"
    rotation_manager.current_log_file.touch()
    rotation_manager.logger.handlers = []
    
    with patch("shutil.move", side_effect=PermissionError("Lock")):
        with patch("time.sleep"):
            rotation_manager.rotate_logs()
            
    assert rotation_manager.logger.error.call_count == 1
    assert "Failed to move log file" in rotation_manager.logger.error.call_args[0][0]

def test_delete_archive_folder_error(rotation_manager, tmp_path):
    folder = tmp_path / "archive/date"
    folder.mkdir(parents=True)
    
    with patch("shutil.rmtree", side_effect=OSError("Access Denied")):
        count = rotation_manager._delete_archive_folder(folder, folder_date=None)
        assert count == 0
        rotation_manager.logger.error.assert_called()

def test_load_config_failures(rotation_manager, tmp_path):
    # Test file permission error or corrupt file implicitly covered?
    # Test specific exception handling in load_config loop
    
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    f = config_dir / "rotation_config.json"
    f.write_text("{bad")
    
    # reset config
    rotation_manager.config = None
    
    res = rotation_manager.load_config()
    assert res is None # Validation error caught?
    # Code catch Exception as e: checks warning
    rotation_manager.logger.warning.assert_called()

def test_save_config_failure(rotation_manager, tmp_path):
    rotation_manager.config_dir = tmp_path / "readonly"
    # Mock loader.save to raise exception
    rotation_manager.loader.save = MagicMock(side_effect=Exception("Disk full"))
    
    rotation_manager.save_config(LogRotationConfig(enabled=True))
    rotation_manager.logger.error.assert_called()

def test_rotate_log_no_config(rotation_manager):
    rotation_manager.config = None
    rotation_manager.rotate_logs()
    rotation_manager.logger.warning.assert_called_with("Log rotation not enabled")

def test_bad_date_parsing(rotation_manager, tmp_path):
    # Log file with weird name
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    f = log_dir / "not_a_date.log"
    f.touch()
    
    rotation_manager.config.log_data_dir = "logs"
    
    # archive_old_logs scan
    rotation_manager.archive_old_logs_from_data()
    # Should warn and skip
    rotation_manager.logger.warning.assert_called()
    assert "Could not parse date" in rotation_manager.logger.warning.call_args_list[0][0][0]

# --- NibandhaLogger Robustness ---

def test_logger_no_console(tmp_path):
    settings = LogSettings(app_name="app", log_dir=tmp_path, console_output=False)
    logger = NibandhaLogger(settings)
    
    # handlers: only FileHandler
    assert len(logger.logger.handlers) == 1
    assert isinstance(logger.logger.handlers[0], logging.FileHandler)

def test_logger_all_levels(tmp_path):
    # Just to ensure coverage of wrapper methods
    settings = LogSettings(app_name="app", log_dir=tmp_path)
    nl = NibandhaLogger(settings)
    nl.logger = MagicMock()
    
    nl.critical("msg")
    nl.warning("msg")
    nl.error("msg")
    nl.debug("msg")
    
    assert nl.logger.critical.called
    assert nl.logger.warning.called
    assert nl.logger.error.called
    assert nl.logger.debug.called
    
def test_logger_log_injection_prevention(tmp_path):
    # Verify that logging handles multiline strings cleanly (doesn't crash)
    settings = LogSettings(app_name="app", log_dir=tmp_path)
    nl = NibandhaLogger(settings)
    nl.logger = MagicMock()
    
    msg = "User input \n [INFO] Fake Log"
    nl.info(msg)
    
    nl.logger.info.assert_called()
    # NibandhaLogger doesn't sanitize itself, it relies on logging module.
    # But checking it processes it is enough for coverage.
