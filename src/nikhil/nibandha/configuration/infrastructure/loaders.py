from typing import Optional, List
from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.configuration.domain.protocols.config_loader import ConfigLoaderProtocol

class StandardConfigLoader:
    """
    Standard loader for AppConfig.
    Currently acts as a builder/factory but can be extended to load from files/env.
    """
    
    def __init__(
        self, 
        name: str, 
        custom_folders: Optional[List[str]] = None, 
        log_level: str = "INFO",
        log_dir: Optional[str] = None,
        report_dir: Optional[str] = None,
        config_dir: Optional[str] = None
    ):
        self.name = name
        self.custom_folders = custom_folders or []
        self.log_level = log_level
        self.log_dir = log_dir
        self.report_dir = report_dir
        self.config_dir = config_dir
        
    def load(self) -> AppConfig:
        """Creates the AppConfig from provided initialization parameters."""
        return AppConfig(
            name=self.name,
            custom_folders=self.custom_folders,
            log_level=self.log_level,
            log_dir=self.log_dir,
            report_dir=self.report_dir,
            config_dir=self.config_dir
        )
