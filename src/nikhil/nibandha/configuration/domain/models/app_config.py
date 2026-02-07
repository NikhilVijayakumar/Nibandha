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
    
    # Root Configuration
    root: Optional['RootConfig'] = Field(None, description="Configuration for the Unified Root")
    
    # Reporting Configuration
    reporting: Optional['ReportingConfig'] = Field(None, description="Configuration for Reporting")
    
    # Logging Configuration
    logging: Optional['LogRotationConfig'] = Field(None, description="Configuration for Log Rotation")

from nibandha.configuration.domain.models.root_config import RootConfig
from nibandha.configuration.domain.models.reporting_config import ReportingConfig
from nibandha.configuration.domain.models.rotation_config import LogRotationConfig
from nibandha.reporting.shared.domain.protocols.module_discovery import ModuleDiscoveryProtocol

ReportingConfig.model_rebuild()
AppConfig.model_rebuild()
