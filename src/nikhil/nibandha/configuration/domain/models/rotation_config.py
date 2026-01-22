from pydantic import BaseModel

class LogRotationConfig(BaseModel):
    """Configuration for log rotation and archival."""
    enabled: bool = False
    max_size_mb: float = 10.0
    rotation_interval_hours: int = 24
    archive_retention_days: int = 30
    backup_count: int = 1  # Number of backup files to keep in archive (in addition to time-based retention)
    log_data_dir: str = "logs/data"
    archive_dir: str = "logs/archive"
    timestamp_format: str = "%Y-%m-%d"
