
import pytest
from unittest.mock import MagicMock, patch, call
from pathlib import Path
from datetime import datetime, timedelta
import logging
import sys
import time

from nibandha.logging.infrastructure.rotation_manager import RotationManager
from nibandha.logging.infrastructure.nibandha_logger import NibandhaLogger
from nibandha.configuration.domain.models.rotation_config import LogRotationConfig
from nibandha.logging.domain.models.log_settings import LogSettings

# --- RotationManager Tests ---

@pytest.fixture
def rotation_manager(tmp_path):
    config_dir = tmp_path / "config"
    app_root = tmp_path
    logger = MagicMock()
    
    manager = RotationManager(config_dir, app_root, logger)
    manager.config = LogRotationConfig(
        enabled=True,
        max_size_mb=1,
        rotation_interval_hours=24,
        archive_retention_days=30,
        backup_count=2,
        log_data_dir="data/logs",
        archive_dir="data/archive"
    )
    return manager

def test_should_rotate_size(rotation_manager, tmp_path):
    # Setup
    log_file = tmp_path / "data/logs/app.log"
    log_file.parent.mkdir(parents=True)
    log_file.write_text("x" * 1024 * 1024 * 2) # 2MB
    
    rotation_manager.current_log_file = log_file
    
    # Check
    assert rotation_manager.should_rotate() == True
    
    # Clean setup for valid check
    assert "exceeds limit" in rotation_manager.logger.info.call_args[0][0]

def test_should_rotate_time(rotation_manager):
    # Setup
    rotation_manager.current_log_file = MagicMock()
    rotation_manager.current_log_file.exists.return_value = True
    rotation_manager.current_log_file.stat.return_value.st_size = 100 # Small
    
    # Old start time
    rotation_manager.log_start_time = datetime.now() - timedelta(hours=25)
    
    assert rotation_manager.should_rotate() == True

def test_rotate_logs(rotation_manager, tmp_path):
    # Setup Log File
    log_dir = tmp_path / "data/logs"
    log_dir.mkdir(parents=True)
    log_file = log_dir / "2023-01-01.log"
    log_file.write_text("content")
    
    rotation_manager.current_log_file = log_file
    
    # Mock Logger Handler
    handler = MagicMock()
    handler.__class__ = logging.FileHandler
    rotation_manager.logger.handlers = [handler]
    
    # Mock DateTime for Archive Name
    with patch("nibandha.logging.infrastructure.rotation_manager.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2023, 1, 2, 12, 0, 0)
        mock_dt.strptime = datetime.strptime # Keep real strptime
        
        # rotation_manager uses datetime logic to parse filename
        # 2023-01-01.log -> 2023-01-01 archive folder
        
        rotation_manager.rotate_logs()
        
    # Verify Archive Exists
    archive = tmp_path / "data/archive/2023-01-01/2023-01-01.log"
    assert archive.exists()
    assert archive.read_text() == "content"
    
    # Verify New Log Created
    # New log name comes from now() -> 2023-01-02.log (mocked)
    new_log = tmp_path / "data/logs/2023-01-02.log"
    # Actually, rotate_logs CREATES a new handler, but pytest mocks file creation of handler?
    # rotation_manager.logger.addHandler(handler) is called with REAL logging.FileHandler
    # We should see if file exists (logging library creates it)
    # But new_log path is correct? log_data_dir is data/logs, format is %Y-%m-%d
    # Mocked timestamp format is %Y-%m-%d? Default is %Y-%m-%d
    
    # logging.FileHandler creates file.
    # To avoid permission issues or mock confusion, we rely on manager.current_log_file update
    assert rotation_manager.current_log_file.name == "2023-01-02.log"

def test_archive_old_logs(rotation_manager, tmp_path):
    log_dir = tmp_path / "data/logs"
    log_dir.mkdir(parents=True)
    
    # Old file
    old = log_dir / "2020-01-01.log"
    old.touch()
    
    # Today file (should stay)
    today_str = datetime.now().strftime("%Y-%m-%d")
    current = log_dir / f"{today_str}.log"
    current.touch()
    
    count = rotation_manager.archive_old_logs_from_data()
    
    assert count == 1
    assert not old.exists()
    assert current.exists()
    assert (tmp_path / "data/archive/2020-01-01/2020-01-01.log").exists()

def test_cleanup_old_archives(rotation_manager, tmp_path):
    archive_dir = tmp_path / "data/archive"
    archive_dir.mkdir(parents=True)
    
    # Create very old archive folder
    old_date = datetime.now() - timedelta(days=100)
    old_folder = archive_dir / old_date.strftime("%Y-%m-%d")
    old_folder.mkdir()
    (old_folder / "log.log").touch()
    
    # Create recent archive folder
    recent_date = datetime.now() - timedelta(days=1)
    recent_folder = archive_dir / recent_date.strftime("%Y-%m-%d")
    recent_folder.mkdir()
    
    # Create excess files in recent folder
    # Limit is 2
    (recent_folder / "1.log").touch()
    time.sleep(0.01)
    (recent_folder / "2.log").touch() # Newer
    time.sleep(0.01)
    (recent_folder / "3.log").touch() # Newest
    
    # Mtimes: 3 > 2 > 1. Sorted reverse: 3, 2, 1. Keep 2. Delete 1.
    
    count = rotation_manager.cleanup_old_archives()
    
    assert count > 0
    assert not old_folder.exists() # Deleted due to retention (30 days)
    assert recent_folder.exists()
    assert len(list(recent_folder.glob("*.log"))) == 2 # 1 deleted

def test_load_save_config(rotation_manager, tmp_path):
    config = LogRotationConfig(enabled=False)
    rotation_manager.save_config(config)
    
    loaded = rotation_manager.load_config()
    assert loaded.enabled == False

def test_prompt_config(rotation_manager):
    with patch("builtins.input", side_effect=["y", "20", "48", "60", "3"]):
        config = rotation_manager.prompt_and_cache_config()
        assert config.enabled == True
        assert config.max_size_mb == 20
        assert config.rotation_interval_hours == 48

# --- NibandhaLogger Tests ---

def test_nibandha_logger_setup(tmp_path):
    settings = LogSettings(
        app_name="testapp",
        log_level="DEBUG",
        rotation_size_mb=5,
        backup_count=1,
        log_dir=tmp_path / "logs",
        console_output=True
    )
    
    logger = NibandhaLogger(settings)
    
    assert logger.logger.level == logging.DEBUG
    assert len(logger.logger.handlers) == 2 # File + Console
    assert (tmp_path / "logs").exists()

def test_nibandha_logger_tracing(tmp_path):
    settings = LogSettings(app_name="traceapp", log_dir=tmp_path)
    logger = NibandhaLogger(settings)
    
    # Mock internal logger
    logger.logger = MagicMock()
    
    logger.info("Test message", ids=["Req1"])
    
    logger.logger.info.assert_called()
    msg = logger.logger.info.call_args[0][0]
    assert "[Req1]" in msg

def test_rotation_error_handling(rotation_manager, tmp_path):
    # Test _delete_file exception
    f = tmp_path / "protected.log"
    f.touch()
    
    with patch.object(Path, "unlink", side_effect=PermissionError("Locked")):
        res = rotation_manager._delete_file(f, "test")
        assert res == 0
        rotation_manager.logger.error.assert_called()
        
    # Test _cleanup_dated_archives non-date folder warning
    archive_dir = tmp_path / "archive"
    archive_dir.mkdir()
    (archive_dir / "random_folder").mkdir()
    
    rotation_manager.config.archive_dir = "archive" # set relative path in config
    # We need to call internal cleanup with the dir
    rotation_manager._cleanup_dated_archives(archive_dir, datetime.now().date())
    
    # Expect warning for non-date folder
    args_list = rotation_manager.logger.warning.call_args_list
    assert any("Non-date folder" in str(Call) for Call in args_list)

