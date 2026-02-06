from pathlib import Path
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field

from nibandha.logging.domain.constants import DEFAULT_BACKUP_COUNT, DEFAULT_MAX_BYTES

class LogSettings(BaseModel):
    """
    Configuration for the Nibandha Logger.
    Immutable settings to prevent runtime tampering.
    """
    model_config = ConfigDict(frozen=True)

    app_name: str = Field(..., description="Identity of the application logging (e.g., 'Amsha')")
    log_dir: Path = Field(..., description="Absolute path to the log directory")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field("INFO", description="Logging level")
    console_output: bool = Field(True, description="Whether to output logs to stdout")
    rotation_size_mb: int = Field(int(DEFAULT_MAX_BYTES / (1024 * 1024)), description="Max size in MB before rotation")
    backup_count: int = Field(DEFAULT_BACKUP_COUNT, description="Number of backup files to keep")
