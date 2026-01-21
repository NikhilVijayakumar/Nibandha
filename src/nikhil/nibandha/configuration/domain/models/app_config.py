from typing import List, Optional
from pydantic import BaseModel, Field

class AppConfig(BaseModel):
    """
    The definition of an app that wants to use Nibandha.
    
    Attributes:
        name: The unique name of the application.
        custom_folders: List of relative paths to create in the app workspace.
        log_level: Python logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_dir: Optional override for the base logs directory.
        report_dir: Optional override for the reports directory.
        config_dir: Optional override for the configuration directory.
    """
    name: str = Field(..., description="Application Name")
    custom_folders: List[str] = Field(default_factory=list, description="Application specific folders")
    log_level: str = Field("INFO", description="Logging Level")
    
    # Path Overrides
    log_dir: Optional[str] = Field(None, description="Override default logs directory")
    report_dir: Optional[str] = Field(None, description="Override default report directory")
    config_dir: Optional[str] = Field(None, description="Override default config directory")
