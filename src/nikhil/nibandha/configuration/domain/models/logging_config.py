from pathlib import Path
from pydantic import BaseModel, Field
from nibandha.logging.domain.constants import (
    DEFAULT_MAX_BYTES, 
    DEFAULT_ROTATION_INTERVAL_HOURS, 
    DEFAULT_RETENTION_DAYS,
    DEFAULT_BACKUP_COUNT
)

class LoggingConfig(BaseModel):
    """Configuration for logging subsystem."""
    level: str = Field("INFO", description="Logging Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    enabled: bool = Field(True, description="Enable logging functionality")
    log_dir: str = Field("logs", description="Relative path for logs")
    
    # Rotation configuration
    rotation_enabled: bool = Field(False, description="Enable log rotation")
    max_size_mb: float = Field(float(DEFAULT_MAX_BYTES / (1024 * 1024)), description="Max log file size in MB")
    rotation_interval_hours: int = Field(DEFAULT_ROTATION_INTERVAL_HOURS, description="Rotation interval in hours")
    archive_retention_days: int = Field(DEFAULT_RETENTION_DAYS, description="Log retention days")
    backup_count: int = Field(DEFAULT_BACKUP_COUNT, description="Number of backups to keep")
    archive_dir: str = Field("logs/archive", description="Archive directory")
    timestamp_format: str = Field("%Y-%m-%d", description="Timestamp format")
