from typing import Protocol, runtime_checkable
from nibandha.configuration.domain.models.app_config import AppConfig
from ..models.root_context import RootContext

@runtime_checkable
class RootBinderProtocol(Protocol):
    """
    Protocol for binding (creating/ensuring) the root directory structure.
    """
    def bind(self, config: AppConfig, root_name: str = ".Nibandha") -> RootContext:
        """
        Calculates paths from config and ensures they exist on the target medium.
        Returns the resolved RootContext.
        """
        ...
