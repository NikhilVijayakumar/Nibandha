from pathlib import Path
from pydantic import BaseModel, Field

class RootContext(BaseModel):
    """
    Immutable resolved context for the application's root structure.
    Represents the 'Physical State' of the workspace.
    """
    root: Path = Field(..., description="The main root (e.g. .Nibandha)")
    app_root: Path = Field(..., description="The application specific root (e.g. .Nibandha/MyApp)")
    config_dir: Path = Field(..., description="Global or resolved config directory")
    log_base: Path = Field(..., description="Base directory for logs")
    report_dir: Path = Field(..., description="Directory for reports")

    class Config:
        frozen = True
