import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.configuration.domain.models.rotation_config import LogRotationConfig
from nibandha.logging.infrastructure.rotation_manager import RotationManager
from nibandha.logging.infrastructure.logger_factory import setup_logger
from nibandha.unified_root.domain.models.root_context import RootContext

class LoggingCoordinator:
    """
    Coordinates the setup and management of logging within the application.
    Encapsulates logic for rotation, logger creation, and internal log capture.
    """

    def __init__(self, config: AppConfig, root_context: Optional[RootContext] = None):
        self.config = config
        self.context = root_context
        self.rotation_manager: Optional[RotationManager] = None
        self.rotation_config: Optional[LogRotationConfig] = None
        self.logger: Optional[logging.Logger] = None
        self.current_log_file: Optional[Path] = None
        self.log_start_time: Optional[datetime] = None

    def initialize_rotation_manager(self, config_dir: Path, app_root: Path, interactive_setup: bool = False) -> LogRotationConfig:
        """Initializes the RotationManager and loads/creates configuration."""
        
        # Temp Logger for RotationManager initialization
        temp_logger = logging.getLogger(self.config.name + "_bootstrap")
        if not temp_logger.handlers:
            ch = logging.StreamHandler()
            ch.setFormatter(logging.Formatter('%(message)s'))
            temp_logger.addHandler(ch)
            temp_logger.setLevel(logging.INFO)

        self.rotation_manager = RotationManager(config_dir, app_root, temp_logger)
        
        # 1. Prefer AppConfig (Unified YAML)
        if hasattr(self.config, 'logging') and self.config.logging:
            self.rotation_config = self.config.logging
            # Also save it to ensure consistency? Maybe not needed if wholly config driven.
            # But RotationManager expects a config file sometimes.
            self.rotation_manager.save_config(self.rotation_config)
            
        # 2. Fallback to RotationManager loading from file
        if not self.rotation_config:
            self.rotation_config = self.rotation_manager.load_config()

        # 3. Interactive Setup or Default Disable
        if not self.rotation_config:
            if interactive_setup:
                self.rotation_config = self.rotation_manager.prompt_and_cache_config()
            else:
                self.rotation_config = LogRotationConfig(enabled=False)
                self.rotation_manager.save_config(self.rotation_config)
        
        return self.rotation_config

    def setup_logging(self, root_context: RootContext):
        """Sets up the main logger and rotation based on the resolved context."""
        self.context = root_context
        
        if self.rotation_config and self.rotation_config.enabled:
            timestamp = datetime.now().strftime(self.rotation_config.timestamp_format)
            log_file = self.context.log_base / self.rotation_config.log_data_dir / f"{timestamp}.log"
            self.current_log_file = log_file
            self.log_start_time = datetime.now()
            
            # Update rotation manager with real paths from context
            if self.rotation_manager:
                self.rotation_manager.current_log_file = self.current_log_file
                self.rotation_manager.log_start_time = self.log_start_time
                self.rotation_manager.app_root = self.context.log_base # Anchor rotation to log base
            
        else:
            log_file = self.context.log_base / "logs" / f"{self.config.name}.log"
            self.current_log_file = log_file

        # Setup Logger
        self.logger = setup_logger(self.config.name, self.config.log_level, log_file)
        
        # Connect Logger to Rotation Manager
        if self.rotation_manager:
            self.rotation_manager.logger = self.logger
        
        # Capture Internal Logs
        self._capture_internal_logs()
        
        self.logger.info(f"Nibandha initialized at {self.context.app_root}")
        
        if self.rotation_config and self.rotation_config.enabled and self.rotation_manager:
            self.logger.info(f"Log rotation enabled: {self.current_log_file.name}")
            self.rotation_manager.archive_old_logs_from_data()
            self.rotation_manager.cleanup_old_archives()

    def _capture_internal_logs(self):
        """Captures internal Nibandha logs and redirects them to the main logger."""
        if not self.logger: return

        internal_logger = logging.getLogger("nibandha")
        internal_logger.setLevel(self.config.log_level)
        for handler in self.logger.handlers:
            if handler not in internal_logger.handlers:
                internal_logger.addHandler(handler)
        internal_logger.propagate = False

    def should_rotate(self) -> bool:
        if not self.rotation_manager: return False
        return self.rotation_manager.should_rotate()

    def rotate_logs(self) -> None:
        if self.rotation_manager:
            self.rotation_manager.rotate_logs()
            self.current_log_file = self.rotation_manager.current_log_file
            self.log_start_time = self.rotation_manager.log_start_time

    def cleanup_old_archives(self) -> int:
        if not self.rotation_manager: return 0
        return self.rotation_manager.cleanup_old_archives()
