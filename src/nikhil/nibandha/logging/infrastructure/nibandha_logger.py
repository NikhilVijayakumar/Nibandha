import logging
import sys
from pathlib import Path
from typing import List, Any
from nibandha.logging.domain.models.log_settings import LogSettings
from nibandha.logging.domain.protocols.logger import LoggerProtocol

class NibandhaLogger:
    """
    Standard Nibandha Logger implementation.
    Wraps standard python logging with structured formatting and ID tracing.
    """
    def __init__(self, settings: LogSettings):
        self.settings = settings
        self.logger = logging.getLogger(settings.app_name)
        self.logger.setLevel(settings.log_level)
        self.logger.propagate = False
        
        # Clear existing handlers
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
            
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | [%(name)s] | %(message)s'
        )
        
        # 1. File Handler
        # Ensure directory exists - allowed only during setup
        if not self.settings.log_dir.exists():
            self.settings.log_dir.mkdir(parents=True, exist_ok=True)
            
        log_file = self.settings.log_dir / f"{self.settings.app_name}.log"
        # Using RotatingFileHandler from standard lib for simplicity in this iteration
        # In a full valid rotation, we might use RotationManager, but sticking to basics first
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=self.settings.rotation_size_mb * 1024 * 1024,
            backupCount=self.settings.backup_count
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # 2. Console Handler
        if self.settings.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def _format_msg(self, msg: str, ids: List[str]) -> str:
        if not ids:
            return msg
        id_str = " ".join([f"[{id_}]" for id_ in ids])
        return f"{msg} {id_str}"

    def debug(self, msg: str, ids: List[str] = [], *args: Any, **kwargs: Any) -> None:
        self.logger.debug(self._format_msg(msg, ids), *args, **kwargs)

    def info(self, msg: str, ids: List[str] = [], *args: Any, **kwargs: Any) -> None:
        self.logger.info(self._format_msg(msg, ids), *args, **kwargs)

    def warning(self, msg: str, ids: List[str] = [], *args: Any, **kwargs: Any) -> None:
        self.logger.warning(self._format_msg(msg, ids), *args, **kwargs)

    def error(self, msg: str, ids: List[str] = [], *args: Any, **kwargs: Any) -> None:
        self.logger.error(self._format_msg(msg, ids), *args, **kwargs)

    def critical(self, msg: str, ids: List[str] = [], *args: Any, **kwargs: Any) -> None:
        self.logger.critical(self._format_msg(msg, ids), *args, **kwargs)
