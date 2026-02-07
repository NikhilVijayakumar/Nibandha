from typing import Protocol, runtime_checkable
from nibandha.configuration.domain.models.app_config import AppConfig

@runtime_checkable
class ConfigLoaderProtocol(Protocol):
    """Protocol for loading application configuration."""
    
    def load(self) -> AppConfig:
        """Load and return the AppConfig."""
        ...
