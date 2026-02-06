from pydantic import BaseModel

from nibandha.logging.domain.constants import (
    DEFAULT_MAX_BYTES, 
    DEFAULT_ROTATION_INTERVAL_HOURS, 
    DEFAULT_RETENTION_DAYS,
    DEFAULT_BACKUP_COUNT
)

class LogRotationConfig(BaseModel):
    """Configuration for log rotation and archival."""
    enabled: bool = False
    max_size_mb: float = float(DEFAULT_MAX_BYTES / (1024 * 1024))
    rotation_interval_hours: int = DEFAULT_ROTATION_INTERVAL_HOURS
    archive_retention_days: int = DEFAULT_RETENTION_DAYS
    backup_count: int = DEFAULT_BACKUP_COUNT  # Number of backup files to keep in archive (in addition to time-based retention)
    log_data_dir: str = "logs/data"
    archive_dir: str = "logs/archive"
    timestamp_format: str = "%Y-%m-%d"
