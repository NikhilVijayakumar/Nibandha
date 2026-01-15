# src/nikhil/nibandha/core.py
import logging
import shutil
import yaml
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel


class AppConfig(BaseModel):
    """The definition of an app that wants to use Nibandha."""
    name: str
    custom_folders: List[str] = []
    log_level: str = "INFO"


class LogRotationConfig(BaseModel):
    """Configuration for log rotation and archival."""
    enabled: bool = False
    max_size_mb: int = 10
    rotation_interval_hours: int = 24
    archive_retention_days: int = 30
    backup_count: int = 1  # Number of backup files to keep in archive (in addition to time-based retention)
    log_data_dir: str = "logs/data"
    archive_dir: str = "logs/archive"
    timestamp_format: str = "%Y-%m-%d"


class Nibandha:
    def __init__(self, config: AppConfig, root_name: str = ".Nibandha"):
        self.config = config
        self.root = Path(root_name)
        self.app_root = self.root / config.name
        self.config_dir = self.root / "config"
        self.rotation_config = None
        self.current_log_file = None
        self.log_start_time = None

    def bind(self):
        """Creates the structure and binds the logger."""
        # Create config directory first
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or prompt for rotation config
        self.rotation_config = self._load_rotation_config()
        if not self.rotation_config:
            self.rotation_config = self._prompt_and_cache_rotation_config()
        
        # Create directory structure based on config
        if self.rotation_config and self.rotation_config.enabled:
            folders = [
                self.rotation_config.log_data_dir,
                self.rotation_config.archive_dir
            ] + self.config.custom_folders
        else:
            folders = ["logs"] + self.config.custom_folders
        
        for folder in folders:
            (self.app_root / folder).mkdir(parents=True, exist_ok=True)
        
        # Setup logger
        self._init_logger()
        return self

    def _load_rotation_config(self) -> Optional[LogRotationConfig]:
        """Load rotation config from .Nibandha/config/rotation_config.{yaml,json}"""
        for ext, loader in [('yaml', yaml.safe_load), ('yml', yaml.safe_load), ('json', json.load)]:
            config_file = self.config_dir / f"rotation_config.{ext}"
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        data = loader(f)
                    return LogRotationConfig(**data)
                except Exception as e:
                    print(f"⚠️  Warning: Failed to load {config_file}: {e}")
        return None

    def _prompt_and_cache_rotation_config(self) -> LogRotationConfig:
        """Prompt user for rotation config and cache it"""
        print("\n📋 Log Rotation Configuration")
        print("=" * 50)
        
        enable = input("Enable log rotation? (y/n) [n]: ").strip().lower()
        if enable != 'y':
            # Cache disabled config
            config = LogRotationConfig(enabled=False)
            self._save_rotation_config(config)
            return config
        
        # Prompt for settings
        max_size = input("Max log size in MB before rotation [10]: ").strip()
        max_size_mb = int(max_size) if max_size else 10
        
        interval = input("Rotation interval in hours [24]: ").strip()
        interval_hours = int(interval) if interval else 24
        
        retention = input("Archive retention in days [30]: ").strip()
        retention_days = int(retention) if retention else 30
        
        backup = input("Number of backup files to keep in archive [1]: ").strip()
        backup_count = int(backup) if backup else 1
        
        config = LogRotationConfig(
            enabled=True,
            max_size_mb=max_size_mb,
            rotation_interval_hours=interval_hours,
            archive_retention_days=retention_days,
            backup_count=backup_count
        )
        
        # Cache config
        self._save_rotation_config(config)
        print(f"✅ Configuration saved to {self.config_dir / 'rotation_config.yaml'}\n")
        
        return config

    def _save_rotation_config(self, config: LogRotationConfig) -> None:
        """Save config to YAML file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        config_file = self.config_dir / "rotation_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config.dict(), f, default_flow_style=False)

    def _init_logger(self):
        """Initialize logging with or without rotation"""
        if self.rotation_config and self.rotation_config.enabled:
            # Create timestamped log file in data directory
            timestamp = datetime.now().strftime(self.rotation_config.timestamp_format)
            log_file = self.app_root / self.rotation_config.log_data_dir / f"{timestamp}.log"
            self.current_log_file = log_file
            self.log_start_time = datetime.now()
        else:
            # Legacy single file
            log_file = self.app_root / "logs" / f"{self.config.name}.log"
        
        # Get the named logger FIRST
        self.logger = logging.getLogger(self.config.name)
        self.logger.setLevel(self.config.log_level)
        
        # Create and attach file handler directly to named logger
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
        )
        
        # Create and attach console handler directly to named logger
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
        )
        
        # Add handlers to the NAMED logger, not ROOT
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Prevent propagation to root logger to avoid duplicate logs
        self.logger.propagate = False
        
        self.logger.info(f"Nibandha initialized at {self.app_root}")
        
        if self.rotation_config and self.rotation_config.enabled:
            self.logger.info(f"Log rotation enabled: {self.current_log_file.name}")

    def should_rotate(self) -> bool:
        """Check if rotation is needed (size OR time trigger)"""
        if not self.rotation_config or not self.rotation_config.enabled:
            return False
        
        if not self.current_log_file or not self.current_log_file.exists():
            return False
        
        # Size check
        size_mb = self.current_log_file.stat().st_size / (1024 * 1024)
        if size_mb >= self.rotation_config.max_size_mb:
            self.logger.info(f"Log size ({size_mb:.2f}MB) exceeds limit ({self.rotation_config.max_size_mb}MB)")
            return True
        
        # Time check
        hours_elapsed = (datetime.now() - self.log_start_time).total_seconds() / 3600
        if hours_elapsed >= self.rotation_config.rotation_interval_hours:
            self.logger.info(f"Log age ({hours_elapsed:.1f}h) exceeds interval ({self.rotation_config.rotation_interval_hours}h)")
            return True
        
        return False

    def rotate_logs(self) -> None:
        """Manually trigger log rotation and archive current log"""
        if not self.rotation_config or not self.rotation_config.enabled:
            self.logger.warning("Log rotation not enabled")
            return
        
        if not self.current_log_file or not self.current_log_file.exists():
            self.logger.warning("No current log file to rotate")
            return
        
        # Close current handlers
        for handler in self.logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                self.logger.removeHandler(handler)
        
        # Move current log to archive
        archive_dir = self.app_root / self.rotation_config.archive_dir
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive_path = archive_dir / self.current_log_file.name
        shutil.move(str(self.current_log_file), str(archive_path))
        
        # Create new timestamped log
        timestamp = datetime.now().strftime(self.rotation_config.timestamp_format)
        new_log = self.app_root / self.rotation_config.log_data_dir / f"{timestamp}.log"
        self.current_log_file = new_log
        self.log_start_time = datetime.now()
        
        # Add new handler
        handler = logging.FileHandler(new_log)
        handler.setFormatter(logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s'))
        self.logger.addHandler(handler)
        
        self.logger.info(f"Log rotated. Archived: {archive_path.name}, New log: {new_log.name}")

    def cleanup_old_archives(self) -> int:
        """Delete archives based on backup_count and retention period. Returns count of deleted files."""
        if not self.rotation_config or not self.rotation_config.enabled:
            return 0
        
        archive_dir = self.app_root / self.rotation_config.archive_dir
        if not archive_dir.exists():
            return 0
        
        deleted_count = 0
        
        # Get all log files sorted by modification time (newest first)
        log_files = sorted(
            archive_dir.glob("*.log"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        
        # Apply backup_count limit (keep only the N most recent backups)
        if len(log_files) > self.rotation_config.backup_count:
            for log_file in log_files[self.rotation_config.backup_count:]:
                log_file.unlink()
                deleted_count += 1
                self.logger.info(f"Deleted old archive (backup limit): {log_file.name}")
        
        # Also apply time-based retention (delete files older than retention period)
        cutoff = datetime.now() - timedelta(days=self.rotation_config.archive_retention_days)
        for log_file in archive_dir.glob("*.log"):
            if not log_file.exists():  # May have been deleted by backup_count limit
                continue
            file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if file_mtime < cutoff:
                log_file.unlink()
                deleted_count += 1
                self.logger.info(f"Deleted old archive (age: {(datetime.now() - file_mtime).days} days): {log_file.name}")
        
        if deleted_count > 0:
            self.logger.info(f"Cleanup complete: {deleted_count} old archives deleted")
        
        return deleted_count