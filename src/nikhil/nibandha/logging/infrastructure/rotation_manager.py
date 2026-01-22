import shutil
import logging
import time
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

from nibandha.configuration.domain.models.rotation_config import LogRotationConfig
from nibandha.configuration.infrastructure.file_loader import FileConfigLoader
from ..domain.protocols.logger import LoggerProtocol

class RotationManager:
    """Manages log rotation configuration and operations."""
    
    def __init__(self, config_dir: Path, app_root: Path, logger: LoggerProtocol):
        self.config_dir = config_dir
        self.app_root = app_root
        self.logger = logger
        self.config: Optional[LogRotationConfig] = None
        self.loader = FileConfigLoader()
        
        # State tracking
        self.current_log_file: Optional[Path] = None
        self.log_start_time: Optional[datetime] = None

    def load_config(self) -> Optional[LogRotationConfig]:
        """Load rotation config from .Nibandha/config/rotation_config.{yaml,json}"""
        # Try YAML first, then JSON
        for ext in ['yaml', 'yml', 'json']:
            config_file = self.config_dir / f"rotation_config.{ext}"
            if config_file.exists():
                try:
                    self.config = self.loader.load(config_file, LogRotationConfig)
                    return self.config
                except Exception as e:
                    self.logger.warning(f"Failed to load {config_file}: {e}")
        return None

    def save_config(self, config: LogRotationConfig) -> None:
        """Save config to YAML file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        config_file = self.config_dir / "rotation_config.yaml"
        try:
            self.loader.save(config_file, config)
            self.config = config
        except Exception as e:
            self.logger.error(f"Failed to save config to {config_file}: {e}")

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
        
        # Move current log to archive with date-based folder structure
        # Small delay to ensure file handles are released (Windows compatibility)
        time.sleep(0.2)
        
        # Extract date from current log filename
        base_name = self.current_log_file.name.split('.log')[0]
        try:
            file_date = datetime.strptime(base_name, self.config.timestamp_format)
            date_str = file_date.strftime(self.config.timestamp_format)
        except ValueError:
            # Fallback to current date if parsing fails
            date_str = datetime.now().strftime(self.config.timestamp_format)
            self.logger.warning(f"Could not parse date from {self.current_log_file.name}, using current date for archive")
        
        # Create date-based archive directory
        archive_date_dir = self.app_root / self.config.archive_dir / date_str
        archive_date_dir.mkdir(parents=True, exist_ok=True)
        
        # Destination path in date folder
        archive_path = archive_date_dir / self.current_log_file.name
        
        # Handle filename collisions (e.g., multiple rotations per day)
        counter = 1
        while archive_path.exists():
            archive_path = archive_date_dir / f"{self.current_log_file.name}.{counter}"
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
        
        self.logger.info(f"Log rotated. Archived: {archive_date_dir.name}/{archive_path.name}, New log: {new_log.name}")


    def archive_old_logs_from_data(self) -> int:
        """Move all non-current logs from data/ to archive/{date}/ folders. Returns count of archived files."""
        if not self.config or not self.config.enabled:
            return 0
        
        data_dir = self.app_root / self.config.log_data_dir
        if not data_dir.exists():
            return 0
        
        # Get today's date for comparison
        today = datetime.now().date()
        today_str = today.strftime(self.config.timestamp_format)
        
        archived_count = 0
        
        # Find all .log files in data directory
        for log_file in data_dir.glob("*.log*"):
            if not log_file.is_file():
                continue
            
            # Extract date from filename
            # Assuming filename format: {date}.log or {date}.log.1, etc.
            base_name = log_file.name.split('.log')[0]
            
            # Try to parse the date from filename
            try:
                file_date = datetime.strptime(base_name, self.config.timestamp_format).date()
            except ValueError:
                # If parsing fails, skip this file (might be a different format)
                self.logger.warning(f"Could not parse date from log file: {log_file.name}, skipping archival")
                continue
            
            # Only archive files that are NOT from today
            if file_date < today:
                # Create date-based archive folder
                date_str = file_date.strftime(self.config.timestamp_format)
                archive_date_dir = self.app_root / self.config.archive_dir / date_str
                archive_date_dir.mkdir(parents=True, exist_ok=True)
                
                # Destination path
                archive_path = archive_date_dir / log_file.name
                
                # Handle name collision (shouldn't happen in date folders, but be safe)
                counter = 1
                while archive_path.exists():
                    archive_path = archive_date_dir / f"{log_file.name}.{counter}"
                    counter += 1
                
                # Move file to archive
                try:
                    shutil.move(str(log_file), str(archive_path))
                    archived_count += 1
                    self.logger.info(f"Archived old log: {log_file.name} -> {archive_date_dir.name}/{archive_path.name}")
                except Exception as e:
                    self.logger.error(f"Failed to archive {log_file.name}: {e}")
        
        if archived_count > 0:
            self.logger.info(f"Daily archival complete: {archived_count} old log(s) moved to archive")
        
        return archived_count

    def cleanup_old_archives(self) -> int:
        """Delete archives based on retention period and backup count. Returns count of deleted files/folders."""
        if not self.config or not self.config.enabled:
            return 0
        
        archive_dir = self.app_root / self.config.archive_dir
        if not archive_dir.exists():
            return 0
        
        deleted_count = 0
        
        # 1. Apply time-based retention: delete entire date folders older than retention period
        cutoff_date = datetime.now().date() - timedelta(days=self.config.archive_retention_days)
        
        for date_folder in archive_dir.iterdir():
            if not date_folder.is_dir():
                continue
            
            # Try to parse the folder name as a date
            try:
                folder_date = datetime.strptime(date_folder.name, self.config.timestamp_format).date()
            except ValueError:
                # Not a date folder, might be legacy flat files - handle separately
                self.logger.warning(f"Non-date folder in archive: {date_folder.name}, skipping")
                continue
            
            # Delete folders older than retention period
            if folder_date < cutoff_date:
                try:
                    # Count files before deletion
                    file_count = len(list(date_folder.glob("*.log*")))
                    shutil.rmtree(date_folder)
                    deleted_count += file_count
                    days_old = (datetime.now().date() - folder_date).days
                    self.logger.info(f"Deleted old archive folder (age: {days_old} days): {date_folder.name}/ ({file_count} file(s))")
                except Exception as e:
                    self.logger.error(f"Failed to delete archive folder {date_folder.name}: {e}")
            else:
                # 2. For folders within retention period, apply backup_count limit per folder
                log_files = sorted(
                    date_folder.glob("*.log*"),
                    key=lambda f: f.stat().st_mtime,
                    reverse=True
                )
                
                if len(log_files) > self.config.backup_count:
                    for log_file in log_files[self.config.backup_count:]:
                        try:
                            log_file.unlink()
                            deleted_count += 1
                            self.logger.info(f"Deleted old archive (backup limit in {date_folder.name}/): {log_file.name}")
                        except Exception as e:
                            self.logger.error(f"Failed to delete {log_file}: {e}")
        
        # 3. Handle legacy flat files in archive root (backward compatibility)
        # These are files NOT in date folders - apply simple backup_count
        flat_files = [f for f in archive_dir.glob("*.log*") if f.is_file()]
        if flat_files:
            self.logger.info(f"Found {len(flat_files)} legacy flat archive files")
            flat_files_sorted = sorted(flat_files, key=lambda f: f.stat().st_mtime, reverse=True)
            
            # Apply backup_count to flat files
            if len(flat_files_sorted) > self.config.backup_count:
                for log_file in flat_files_sorted[self.config.backup_count:]:
                    try:
                        log_file.unlink()
                        deleted_count += 1
                        self.logger.info(f"Deleted old legacy archive (backup limit): {log_file.name}")
                    except Exception as e:
                        self.logger.error(f"Failed to delete {log_file}: {e}")
            
            # Also apply time-based retention to flat files
            cutoff_datetime = datetime.now() - timedelta(days=self.config.archive_retention_days)
            for log_file in archive_dir.glob("*.log*"):
                if not log_file.is_file() or not log_file.exists():
                    continue
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_mtime < cutoff_datetime:
                    try:
                        log_file.unlink()
                        deleted_count += 1
                        days_old = (datetime.now() - file_mtime).days
                        self.logger.info(f"Deleted old legacy archive (age: {days_old} days): {log_file.name}")
                    except Exception as e:
                        self.logger.error(f"Failed to delete {log_file}: {e}")
        
        if deleted_count > 0:
            self.logger.info(f"Cleanup complete: {deleted_count} old archive(s) deleted")
        
        return deleted_count
