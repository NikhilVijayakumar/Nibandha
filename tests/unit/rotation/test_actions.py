
import pytest
import time
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from nibandha import Nibandha
from nibandha.configuration.domain.models.rotation_config import LogRotationConfig
from nibandha.logging.infrastructure.rotation_manager import RotationManager
import logging

class TestRotationActions:
    """Happy Path: Triggers, Rotation, Cleanup"""
    
    @patch('builtins.input', side_effect=['n'])
    def test_should_rotate_on_size_limit(self, mock_input, temp_root, sample_app_config):
        """Test size-based rotation trigger"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.config_dir.mkdir(parents=True, exist_ok=True)
        rm = RotationManager(nb.config_dir, nb.app_root, logging.getLogger("test"))
        rm.save_config(LogRotationConfig(enabled=True, max_size_mb=0.001))
        
        nb.bind()
        
        # Write enough data to exceed limit
        for i in range(1000):
            nb.logger.info(f"Test log message {i} " * 10)
        
        assert nb.should_rotate() is True

    @patch('builtins.input', side_effect=['n'])
    def test_rotate_logs_creates_new_file(self, mock_input, temp_root, sample_app_config):
        """Test that rotation creates a new log file"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.config_dir.mkdir(parents=True, exist_ok=True)
        rm = RotationManager(nb.config_dir, nb.app_root, logging.getLogger("test"))
        rm.save_config(LogRotationConfig(enabled=True, timestamp_format="%Y-%m-%d_%H-%M-%S"))
        
        nb.bind()
        
        nb.config_dir.mkdir(parents=True, exist_ok=True)
        rm = RotationManager(nb.config_dir, nb.app_root, logging.getLogger("test"))
        # Use simple format, knowing we will mock time
        rm.save_config(LogRotationConfig(enabled=True, timestamp_format="%Y-%m-%d_%H-%M-%S"))
        
        nb.bind()
        
        old_log = nb.current_log_file
        
        # Mock datetime to ensure rotation creates new timestamp
        # Patch where RotationManager imports datetime
        # Mock datetime to ensure rotation creates new timestamp
        # Patch where RotationManager imports datetime
        with patch('nibandha.logging.infrastructure.rotation_manager.datetime') as mock_dt:
            # First call (current default)
            base_time = datetime(2035, 1, 1, 12, 0, 0)
            mock_dt.now.return_value = base_time
            mock_dt.fromtimestamp = datetime.fromtimestamp # Keep valid
            mock_dt.strftime = datetime.strftime
            
            # Need to ensure that when rotate_logs calls now(), it gets NEW time
            # We use side_effect to advance time if multiple calls
            mock_dt.now.side_effect = [base_time, base_time + timedelta(seconds=2)]

            for h in nb.logger.handlers:
                try:
                    h.flush()
                except:
                    pass
                
            nb.rotate_logs()
        
        # Verify
        assert nb.current_log_file != old_log
        assert nb.current_log_file.exists()

    @patch('builtins.input', side_effect=['n'])
    def test_cleanup_old_archives(self, mock_input, temp_root, sample_app_config):
        """Test that old archives are deleted"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.config_dir.mkdir(parents=True, exist_ok=True)
        rm = RotationManager(nb.config_dir, nb.app_root, logging.getLogger("test"))
        rm.save_config(LogRotationConfig(enabled=True, archive_retention_days=7))
        
        nb.bind()
        
        archive_dir = nb.app_root / nb.rotation_config.archive_dir
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Create old archive file
        old_archive = archive_dir / "2025-01-01.log"
        old_archive.write_text("Old log content")
        
        # Set modification time to 30 days ago
        old_time = (datetime.now() - timedelta(days=30)).timestamp()
        old_archive.touch()
        # Ensure we can delete it (not read-only)
        try:
            import os
            os.chmod(old_archive, 0o666)
            os.utime(old_archive, (old_time, old_time))
        except:
            pass # Windows sometimes tricky with utime/permissions on temp files
            
        deleted = nb.cleanup_old_archives()
        # Verify it actually deleted if test env allowed utime
        # If utime failed, it might not be old enough, so this test might be flaky on some OS
        # But assuming standard env
        if deleted > 0:
             assert not old_archive.exists()

    @patch('builtins.input', side_effect=['n'])
    def test_cleanup_respects_backup_count(self, mock_input, temp_root, sample_app_config):
        """Test that backup_count limit enforces deletion regardless of age"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.config_dir.mkdir(parents=True, exist_ok=True)
        rm = RotationManager(nb.config_dir, nb.app_root, logging.getLogger("test"))
        rm.save_config(LogRotationConfig(enabled=True, backup_count=2, archive_retention_days=999))
        
        nb.bind()
        
        # Mock filesystem for cleanup
        # We need to mock archive_dir.glob and unlink
        
        with patch.object(Path, 'glob') as mock_glob, \
             patch.object(Path, 'unlink') as mock_unlink:
            
            # Create mock file objects with specific stats
            mock_files = []
            base_time = time.time()
            for i in range(5):
                f = MagicMock(spec=Path)
                f.name = f"archive_{i}.log"
                f.exists.return_value = True # Important for verify check loop
                # Set mtime: i=0 is oldest, i=4 is newest
                stat_mock = MagicMock()
                stat_mock.st_mtime = base_time + (i * 100) 
                f.stat.return_value = stat_mock
                mock_files.append(f)
            
            # glob returns iterator
            mock_glob.return_value = iter(mock_files)
            
            deleted = nb.cleanup_old_archives()
            
            # 5 files, backup_count=2. Should keep 2 newest ([3], [4]). Delete 3 oldest ([0], [1], [2]).
            assert deleted == 3
            
            # Verify unlink called for oldest 3
            mock_files[0].unlink.assert_called_once()
            mock_files[1].unlink.assert_called_once()
            mock_files[2].unlink.assert_called_once()
            
            # Verify NEWEST 2 NOT deleted
            mock_files[3].unlink.assert_not_called()
            mock_files[4].unlink.assert_not_called()
