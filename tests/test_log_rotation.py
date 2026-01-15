import pytest
import yaml
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from nibandha.core import Nibandha, AppConfig, LogRotationConfig


class TestConfigurationLoading:
    """Test configuration loading from YAML/JSON files"""
    
    def test_load_cached_config_yaml(self, temp_root, sample_app_config):
        """Test loading existing YAML config"""
        config_dir = Path(temp_root) / ".Nibandha" / "config"
        config_dir.mkdir(parents=True)
        
        # Create YAML config
        config_file = config_dir / "rotation_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump({
                'enabled': True,
                'max_size_mb': 50,
                'rotation_interval_hours': 48,
                'archive_retention_days': 60
            }, f)
        
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        config = nb._load_rotation_config()
        
        assert config is not None
        assert config.enabled is True
        assert config.max_size_mb == 50
        assert config.rotation_interval_hours == 48
        assert config.archive_retention_days == 60
    
    def test_load_cached_config_json(self, temp_root, sample_app_config):
        """Test loading existing JSON config"""
        config_dir = Path(temp_root) / ".Nibandha" / "config"
        config_dir.mkdir(parents=True)
        
        # Create JSON config
        config_file = config_dir / "rotation_config.json"
        with open(config_file, 'w') as f:
            json.dump({
                'enabled': True,
                'max_size_mb': 25,
                'rotation_interval_hours': 12,
                'archive_retention_days': 14
            }, f)
        
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        config = nb._load_rotation_config()
        
        assert config is not None
        assert config.enabled is True
        assert config.max_size_mb == 25
    
    def test_no_config_returns_none(self, temp_root, sample_app_config):
        """Test that missing config returns None"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        config = nb._load_rotation_config()
        assert config is None
    
    def test_save_rotation_config(self, temp_root, sample_app_config):
        """Test saving config to YAML file"""
        config_dir = Path(temp_root) / ".Nibandha" / "config"
        config_dir.mkdir(parents=True)
        
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        test_config = LogRotationConfig(enabled=True, max_size_mb=100)
        nb._save_rotation_config(test_config)
        
        config_file = config_dir / "rotation_config.yaml"
        assert config_file.exists()
        
        with open(config_file, 'r') as f:
            data = yaml.safe_load(f)
        assert data['enabled'] is True
        assert data['max_size_mb'] == 100


class TestInteractivePrompting:
    """Test interactive configuration prompting"""
    
    @patch('builtins.input', side_effect=['n'])
    def test_prompt_disabled_rotation(self, mock_input, temp_root, sample_app_config):
        """Test prompting when user disables rotation"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.config_dir.mkdir(parents=True)
        
        config = nb._prompt_and_cache_rotation_config()
        
        assert config.enabled is False
        assert (nb.config_dir / "rotation_config.yaml").exists()
    
    @patch('builtins.input', side_effect=['y', '25', '12', '90'])
    def test_prompt_enabled_with_customs(self, mock_input, temp_root, sample_app_config):
        """Test prompting with custom values"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.config_dir.mkdir(parents=True)
        
        config = nb._prompt_and_cache_rotation_config()
        
        assert config.enabled is True
        assert config.max_size_mb == 25
        assert config.rotation_interval_hours == 12
        assert config.archive_retention_days == 90
    
    @patch('builtins.input', side_effect=['y', '', '', ''])
    def test_prompt_uses_defaults(self, mock_input, temp_root, sample_app_config):
        """Test prompting uses default values when empty input"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.config_dir.mkdir(parents=True)
        
        config = nb._prompt_and_cache_rotation_config()
        
        assert config.enabled is True
        assert config.max_size_mb == 10
        assert config.rotation_interval_hours == 24
        assert config.archive_retention_days == 30


class TestDirectoryStructure:
    """Test directory creation based on config"""
    
    @patch('builtins.input', side_effect=['n'])
    def test_creates_data_and_archive_dirs_when_enabled(self, mock_input, temp_root, sample_app_config):
        """Test that data and archive dirs are created when rotation enabled"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        
        # Manually set enabled config
        nb.rotation_config = LogRotationConfig(enabled=True)
        nb._save_rotation_config(nb.rotation_config)
        
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.bind()
        
        assert (nb.app_root / "logs/data").exists()
        assert (nb.app_root / "logs/archive").exists()
    
    @patch('builtins.input', side_effect=['n'])
    def test_fallback_to_logs_dir_when_disabled(self, mock_input, temp_root, sample_app_config):
        """Test legacy logs directory when rotation disabled"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.bind()
        
        assert (nb.app_root / "logs").exists()
        assert not (nb.app_root / "logs/data").exists()


class TestTimestampedLogs:
    """Test timestamped log file creation"""
    
    @patch('builtins.input', side_effect=['n'])
    def test_creates_timestamped_log_file(self, mock_input, temp_root, sample_app_config):
        """Test that log files have timestamp format when rotation enabled"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.rotation_config = LogRotationConfig(enabled=True)
        nb._save_rotation_config(nb.rotation_config)
        
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.bind()
        
        assert nb.current_log_file is not None
        assert nb.current_log_file.exists()
        assert ".log" in nb.current_log_file.name
        # Verify timestamp format (e.g., 2026-01-15.log)
        assert len(nb.current_log_file.stem) == 10  # YYYY-MM-DD


class TestRotationTriggers:
    """Test rotation trigger logic"""
    
    @patch('builtins.input', side_effect=['n'])
    def test_should_rotate_on_size_limit(self, mock_input, temp_root, sample_app_config):
        """Test size-based rotation trigger"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.rotation_config = LogRotationConfig(enabled=True, max_size_mb=0.001)  # Very small
        nb._save_rotation_config(nb.rotation_config)
        
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.bind()
        
        # Write enough data to exceed limit
        for i in range(1000):
            nb.logger.info(f"Test log message {i} " * 10)
        
        assert nb.should_rotate() is True
    
    @patch('builtins.input', side_effect=['n'])
    def test_should_rotate_on_time_limit(self, mock_input, temp_root, sample_app_config):
        """Test time-based rotation trigger"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.rotation_config = LogRotationConfig(enabled=True, rotation_interval_hours=0.001)  # Very short
        nb._save_rotation_config(nb.rotation_config)
        
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.bind()
        
        # Wait a bit
        time.sleep(0.1)
        
        assert nb.should_rotate() is True
    
    @patch('builtins.input', side_effect=['n'])
    def test_should_not_rotate_when_disabled(self, mock_input, temp_root, sample_app_config):
        """Test that rotation check returns False when disabled"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.bind()
        
        assert nb.should_rotate() is False


class TestLogRotation:
    """Test log rotation functionality"""
    
    @patch('builtins.input', side_effect=['n'])
    def test_rotate_logs_creates_new_file(self, mock_input, temp_root, sample_app_config):
        """Test that rotation creates a new log file"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.rotation_config = LogRotationConfig(enabled=True)
        nb._save_rotation_config(nb.rotation_config)
        
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.bind()
        
        old_log = nb.current_log_file
        nb.logger.info("Before rotation")
        
        time.sleep(0.1)  # Small delay to ensure different timestamp
        nb.rotate_logs()
        
        assert nb.current_log_file != old_log
        assert nb.current_log_file.exists()
    
    @patch('builtins.input', side_effect=['n'])
    def test_rotate_logs_moves_to_archive(self, mock_input, temp_root, sample_app_config):
        """Test that old log is moved to archive"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.rotation_config = LogRotationConfig(enabled=True)
        nb._save_rotation_config(nb.rotation_config)
        
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.bind()
        
        old_log_name = nb.current_log_file.name
        nb.logger.info("Test message")
        
        time.sleep(0.1)
        nb.rotate_logs()
        
        archive_dir = nb.app_root / nb.rotation_config.archive_dir
        assert (archive_dir / old_log_name).exists()


class TestArchiveCleanup:
    """Test archive cleanup functionality"""
    
    @patch('builtins.input', side_effect=['n'])
    def test_cleanup_old_archives(self, mock_input, temp_root, sample_app_config):
        """Test that old archives are deleted"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.rotation_config = LogRotationConfig(enabled=True, archive_retention_days=7)
        nb._save_rotation_config(nb.rotation_config)
        
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.bind()
        
        archive_dir = nb.app_root / nb.rotation_config.archive_dir
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Create old archive file
        old_archive = archive_dir / "2025-01-01.log"
        old_archive.write_text("Old log content")
        
        # Set modification time to 30 days ago
        old_time = (datetime.now() - timedelta(days=30)).timestamp()
        old_archive.touch()
        old_archive.chmod(0o666)
        import os
        os.utime(old_archive, (old_time, old_time))
        
        deleted = nb.cleanup_old_archives()
        
        assert deleted == 1
        assert not old_archive.exists()
    
    @patch('builtins.input', side_effect=['n'])
    def test_cleanup_preserves_recent_files(self, mock_input, temp_root, sample_app_config):
        """Test that recent files are preserved"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.rotation_config = LogRotationConfig(enabled=True, archive_retention_days=7)
        nb._save_rotation_config(nb.rotation_config)
        
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.bind()
        
        archive_dir = nb.app_root / nb.rotation_config.archive_dir
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Create recent archive file
        recent_archive = archive_dir / "2026-01-13.log"
        recent_archive.write_text("Recent log content")
        
        deleted = nb.cleanup_old_archives()
        
        assert deleted == 0
        assert recent_archive.exists()


class TestBackwardsCompatibility:
    """Test backwards compatibility with existing code"""
    
    @patch('builtins.input', side_effect=['n'])
    def test_legacy_single_log_file(self, mock_input, temp_root, sample_app_config):
        """Test that legacy single log file works when rotation disabled"""
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        nb.bind()
        
        log_file = nb.app_root / "logs" / f"{sample_app_config.name}.log"
        assert log_file.exists()
        assert nb.current_log_file is None  # No rotation tracking
