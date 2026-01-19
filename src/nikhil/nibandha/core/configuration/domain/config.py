from typing import List, Optional
from pydantic import BaseModel

class AppConfig(BaseModel):
    """The definition of an app that wants to use Nibandha."""
    name: str
    custom_folders: List[str] = []
    log_level: str = "INFO"
    # Path Overrides
    log_dir: Optional[str] = None  # Override default logs directory
    report_dir: Optional[str] = None # Override default report directory
    config_dir: Optional[str] = None # Override default config directory
