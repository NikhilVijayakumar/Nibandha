from typing import List, Optional
from pydantic import BaseModel, Field

class CoreConfig(BaseModel):
    """
    Core configuration for the application.
    Identifies the application and its basic runtime parameters.
    """
    name: str = Field(..., description="Application Name")
    mode: str = Field("production", description="Operating Mode (dev/prod)")
    log_level: str = Field("INFO", description="Logging Level")
    custom_folders: List[str] = Field(default_factory=list, description="Application specific folders")
    
    # Path Overrides
    log_dir: Optional[str] = Field(None, description="Override default logs directory")
    report_dir: Optional[str] = Field(None, description="Override default report directory")
    config_dir: Optional[str] = Field(None, description="Override default config directory")
