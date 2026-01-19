import shutil
import yaml
import json
import logging
import time
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

from ..domain.config import LogRotationConfig
from ...logging.domain.protocols import LoggerProtocol

class RotationManager:
    """Manages log rotation configuration and operations."""
    
    def __init__(self, config_dir: Path, app_root: Path, logger: LoggerProtocol):
        self.config_dir = config_dir
        self.app_root = app_root
        self.logger = logger
        self.config: Optional[LogRotationConfig] = None
        
        # State tracking
        self.current_log_file: Optional[Path] = None
        self.log_start_time: Optional[datetime] = None

    def load_config(self) -> Optional[LogRotationConfig]:
        """Load rotation config from .Nibandha/config/rotation_config.{yaml,json}"""
        for ext, loader in [('yaml', yaml.safe_load), ('yml', yaml.safe_load), ('json', json.load)]:
            config_file = self.config_dir / f"rotation_config.{ext}"
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        data = loader(f)
                    self.config = LogRotationConfig(**data)
                    return self.config
                except Exception as e:
                    self.logger.warning(f"Failed to load {config_file}: {e}")
        return None

    def save_config(self, config: LogRotationConfig) -> None:
        """Save config to YAML file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        config_file = self.config_dir / "rotation_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config.dict(), f, default_flow_style=False)
        self.config = config

    def prompt_and_cache_config(self) -> LogRotationConfig:
        """Prompt user for rotation config and cache it"""
        self.logger.info("\n📋 Log Rotation Configuration")
        self.logger.info("=" * 50)
        
        enable = input("Enable log rotation? (y/n) [n]: ").strip().lower()
        if enable != 'y':
            # Cache disabled config
            config = LogRotationConfig(enabled=False)
            self.save_config(config)
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
        self.save_config(config)
        self.logger.info(f"✅ Configuration saved to {self.config_dir / 'rotation_config.yaml'}\n")
        
        return config

    def should_rotate(self) -> bool:
        """Check if rotation is needed (size OR time trigger)"""
        if not self.config or not self.config.enabled:
            return False
        
        if not self.current_log_file or not self.current_log_file.exists():
            return False
        
        # Size check
        size_mb = self.current_log_file.stat().st_size / (1024 * 1024)
        if size_mb >= self.config.max_size_mb:
            self.logger.info(f"Log size ({size_mb:.2f}MB) exceeds limit ({self.config.max_size_mb}MB)")
            return True
        
        # Time check
        if self.log_start_time:
            hours_elapsed = (datetime.now() - self.log_start_time).total_seconds() / 3600
            if hours_elapsed >= self.config.rotation_interval_hours:
                self.logger.info(f"Log age ({hours_elapsed:.1f}h) exceeds interval ({self.config.rotation_interval_hours}h)")
                return True
        
        return False

    def rotate_logs(self) -> None:
        """Manually trigger log rotation and archive current log"""
        if not self.config or not self.config.enabled:
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
        # Small delay to ensure file handles are released (Windows compatibility)
        time.sleep(0.2)
        
        archive_dir = self.app_root / self.config.archive_dir
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Handle filename collisions (e.g., multiple rotations per day)
        base_name = self.current_log_file.name
        archive_path = archive_dir / base_name
        
        counter = 1
        while archive_path.exists():
            archive_path = archive_dir / f"{base_name}.{counter}"
            counter += 1
        
        # Retry loop for Windows file locking
        for i in range(3):
            try:
                shutil.move(str(self.current_log_file), str(archive_path))
                break
            except PermissionError:
                if i == 2:
                    self.logger.error(f"Failed to move log file after 3 attempts: {self.current_log_file}")
                    return # Stop rotation if move fails
                time.sleep(0.5)
        
        # Create new timestamped log
        # NOTE: Caller (Application) needs to re-initialize logger or we handle it here?
        # Ideally, this manager shouldn't know about creating new handlers attached to app logger...
        # But it needs to setup the new file.
        
        timestamp = datetime.now().strftime(self.config.timestamp_format)
        new_log = self.app_root / self.config.log_data_dir / f"{timestamp}.log"
        self.current_log_file = new_log
        self.log_start_time = datetime.now()
        
        # Add new handler
        handler = logging.FileHandler(new_log)
        handler.setFormatter(logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s'))
        self.logger.addHandler(handler)
        
        self.logger.info(f"Log rotated. Archived: {archive_path.name}, New log: {new_log.name}")

    def cleanup_old_archives(self) -> int:
        """Delete archives based on backup_count and retention period. Returns count of deleted files."""
        if not self.config or not self.config.enabled:
            return 0
        
        archive_dir = self.app_root / self.config.archive_dir
        if not archive_dir.exists():
            return 0
        
        deleted_count = 0
        
        # Get all log files sorted by modification time (newest first)
        # Match .log and .log.1, .log.2 etc
        log_files = sorted(
            archive_dir.glob("*.log*"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        
        # Apply backup_count limit (keep only the N most recent backups)
        if len(log_files) > self.config.backup_count:
            for log_file in log_files[self.config.backup_count:]:
                log_file.unlink()
                deleted_count += 1
                self.logger.info(f"Deleted old archive (backup limit): {log_file.name}")
        
        # Also apply time-based retention (delete files older than retention period)
        cutoff = datetime.now() - timedelta(days=self.config.archive_retention_days)
        for log_file in archive_dir.glob("*.log*"):
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
