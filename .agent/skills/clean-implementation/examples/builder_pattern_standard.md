Example: Fluent Builder Pattern (Gold Standard)
This demonstrates how a Doc-Architect requirement is turned into a Clean Architecture implementation with a Fluent API.

Python

from nibandha.domain.models.archiver_settings import ArchiverSettings
from nibandha.domain.protocols.logger_protocol import LoggerProtocol
from nibandha.archiver.core import Archiver

class ArchiverBuilder:
    """Fluent Builder for the Archiver library."""
    
    def __init__(self):
        self._settings = None
        self._logger = None

    def with_settings(self, settings: ArchiverSettings) -> 'ArchiverBuilder':
        self._settings = settings
        return self

    def with_logger(self, logger: LoggerProtocol) -> 'ArchiverBuilder':
        self._logger = logger
        return self

    def build(self) -> Archiver:
        if not self._settings or not self._logger:
            raise ValueError("ArchiverBuilder: Settings and Logger are required.")
        
        # Returns the immutable, injected instance
        return Archiver(settings=self._settings, logger=self._logger)