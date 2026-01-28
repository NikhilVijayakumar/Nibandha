
import pytest
import shutil
import time
from pathlib import Path
from datetime import datetime, timedelta
from nibandha import Nibandha
from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.configuration.domain.models.rotation_config import LogRotationConfig
from nibandha.logging.infrastructure.rotation_manager import RotationManager
import logging

class TestDailyArchival:
    """Test automatic daily archival with date-based folder structure"""
    
    def test_archive_old_logs_moves_to_date_folders(self, temp_root, sample_app_config):
        """Test that old logs are moved to archive/{date}/ folders"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        
        # Setup rotation config
        rot_config = LogRotationConfig(
            enabled=True,
            timestamp_format="%Y-%m-%d",
            log_data_dir="data",
            archive_dir="archive"
        )
        nb.config_dir.mkdir(parents=True, exist_ok=True)
        rm = RotationManager(nb.config_dir, nb.app_root, logging.getLogger("test"))
        rm.save_config(rot_config)
        
        # Bind to create structure
        nb.bind()
        
        # Create fake old log files in data/
        data_dir = nb.log_base / "data"
        today = datetime.now().date()
        
        # Create logs from different days
        dates = [
            today - timedelta(days=5),  # 5 days ago
            today - timedelta(days=3),  # 3 days ago
            today - timedelta(days=1),  # yesterday
        ]
        
        for date in dates:
            log_file = data_dir / f"{date.strftime('%Y-%m-%d')}.log"
            log_file.write_text(f"Old log from {date}")
        
        # Current log should exist
        current_log = data_dir / f"{today.strftime('%Y-%m-%d')}.log"
        assert current_log.exists()
        
        # Run archival
        archived_count = nb.rotation_manager.archive_old_logs_from_data()
        
        # Verify old logs moved to date folders
        assert archived_count == 3
        
        # Check archive structure
        archive_dir = nb.log_base / "archive"
        for date in dates:
            date_str = date.strftime('%Y-%m-%d')
            date_folder = archive_dir / date_str
            assert date_folder.exists()
            assert (date_folder / f"{date_str}.log").exists()
        
        # Current log should still be in data/
        assert current_log.exists()
        
    def test_cleanup_respects_retention_days(self, temp_root, sample_app_config):
        """Test that cleanup deletes entire date folders older than retention period"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        
        # Setup rotation config with 7-day retention
        rot_config = LogRotationConfig(
            enabled=True,
            archive_retention_days=7,
            timestamp_format="%Y-%m-%d"
        )
        nb.config_dir.mkdir(parents=True, exist_ok=True)
        rm = RotationManager(nb.config_dir, nb.app_root, logging.getLogger("test"))
        rm.save_config(rot_config)
        
        nb.bind()
        
        # Create archive folders with different dates
        # FIX: Matches default "logs/archive"
        archive_dir = nb.log_base / "logs/archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        today = datetime.now().date()
        
        dates = [
            today - timedelta(days=10),  # Should be deleted (> 7 days)
            today - timedelta(days=8),   # Should be deleted (> 7 days)
            today - timedelta(days=5),   # Should be kept (< 7 days)
            today - timedelta(days=2),   # Should be kept (< 7 days)
        ]
        
        for date in dates:
            date_str = date.strftime('%Y-%m-%d')
            date_folder = archive_dir / date_str
            date_folder.mkdir(parents=True, exist_ok=True)
            (date_folder / f"{date_str}.log").write_text(f"Archive from {date}")
            (date_folder / f"{date_str}.log").write_text(f"Archive from {date}")
            # Ensure different mtimes for reliable sorting in cleanup
            time.sleep(0.01)
        
        # Run cleanup
        deleted_count = nb.cleanup_old_archives()
        
        # Verify old folders deleted
        assert deleted_count == 2  # Two old folders
        assert not (archive_dir / dates[0].strftime('%Y-%m-%d')).exists()
        assert not (archive_dir / dates[1].strftime('%Y-%m-%d')).exists()
        
        # Verify recent folders kept
        assert (archive_dir / dates[2].strftime('%Y-%m-%d')).exists()
        assert (archive_dir / dates[3].strftime('%Y-%m-%d')).exists()
    
    def test_cleanup_respects_backup_count_per_folder(self, temp_root, sample_app_config):
        """Test that backup_count is applied per date folder"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        
        # Setup rotation config with backup_count=2
        rot_config = LogRotationConfig(
            enabled=True,
            backup_count=2,
            archive_retention_days=30,
            timestamp_format="%Y-%m-%d"
        )
        nb.config_dir.mkdir(parents=True, exist_ok=True)
        rm = RotationManager(nb.config_dir, nb.app_root, logging.getLogger("test"))
        rm.save_config(rot_config)
        
        nb.bind()
        
        # Create a date folder with multiple log files
        # FIX: Matches default "logs/archive"
        archive_dir = nb.log_base / "logs/archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        yesterday = datetime.now().date() - timedelta(days=1)
        date_str = yesterday.strftime('%Y-%m-%d')
        date_folder = archive_dir / date_str
        date_folder.mkdir(parents=True, exist_ok=True)
        
        # Create 5 log files in the same date folder
        for i in range(5):
            log_file = date_folder / f"{date_str}.log.{i}"
            log_file.write_text(f"Log {i}")
            # Add small delay to ensure different mtimes
            time.sleep(0.01)
        
        # Run cleanup
        deleted_count = nb.cleanup_old_archives()
        
        # Should keep only 2 most recent files
        remaining_files = list(date_folder.glob("*.log*"))
        assert len(remaining_files) == 2
        assert deleted_count == 3
        
        # Verify the kept files are the most recent ones
        assert (date_folder / f"{date_str}.log.4").exists()
        assert (date_folder / f"{date_str}.log.3").exists()
    
    def test_automatic_archival_on_startup(self, temp_root, sample_app_config):
        """Test that archival and cleanup run automatically on bind()"""
        # Create first instance with old logs
        nb1 = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        
        rot_config = LogRotationConfig(
            enabled=True,
            archive_retention_days=3,
            timestamp_format="%Y-%m-%d"
        )
        nb1.config_dir.mkdir(parents=True, exist_ok=True)
        rm = RotationManager(nb1.config_dir, nb1.app_root, logging.getLogger("test"))
        rm.save_config(rot_config)
        
        nb1.bind()
        
        # Manually create old logs in data/
        # FIX: Matches default "logs/data" 
        data_dir = nb1.log_base / "logs/data"
        if not data_dir.exists():
            data_dir.mkdir(parents=True, exist_ok=True)
            
        today = datetime.now().date()
        old_date = today - timedelta(days=2)
        old_log = data_dir / f"{old_date.strftime('%Y-%m-%d')}.log"
        old_log.write_text("Old log")
        
        # Create a new instance (simulates restart)
        nb2 = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb2.bind()  # Should automatically archive old logs
        
        # Verify old log was archived
        # Ensure config was loaded and enabled
        assert nb2.rotation_config, "Rotation config wasn't loaded"
        assert nb2.rotation_config.enabled, "Rotation is disabled"
        
        assert not old_log.exists(), f"Old log still exists at {old_log}"
        
        # Matches default "logs/archive"
        archive_dir = nb2.log_base / "logs/archive"
        archived_log = archive_dir / old_date.strftime('%Y-%m-%d') / f"{old_date.strftime('%Y-%m-%d')}.log"
        assert archived_log.exists()
    
    def test_handles_invalid_date_filenames_gracefully(self, temp_root, sample_app_config):
        """Test that non-date files are skipped gracefully"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        
        rot_config = LogRotationConfig(enabled=True)
        nb.config_dir.mkdir(parents=True, exist_ok=True)
        rm = RotationManager(nb.config_dir, nb.app_root, logging.getLogger("test"))
        rm.save_config(rot_config)
        
        nb.bind()
        
        # Create files with invalid date formats
        data_dir = nb.log_base / "data"
        if not data_dir.exists():
            data_dir.mkdir(parents=True)
        invalid_file = data_dir / "invalid_name.log"
        invalid_file.write_text("Invalid log")
        
        # Should not crash, just skip
        archived_count = nb.rotation_manager.archive_old_logs_from_data()
        assert archived_count == 0
        assert invalid_file.exists()  # Still in data/
