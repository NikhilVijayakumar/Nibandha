from pathlib import Path
from datetime import datetime
import logging
from typing import Optional

from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.logging.domain.models.rotation_config import LogRotationConfig
from nibandha.logging.infrastructure.rotation_manager import RotationManager
from nibandha.logging.infrastructure.logger_factory import setup_logger

from .domain.models.root_context import RootContext
from .domain.protocols.root_binder import RootBinderProtocol
from .infrastructure.filesystem_binder import FileSystemBinder

class Nibandha:
    """
    Application Facade (Clean Architecture).
    Orchestrates the binding of configuration, filesystem, and logging.
    """
    def __init__(self, config: AppConfig, root_name: str = ".Nibandha", binder: RootBinderProtocol = None):
        self.config = config
        self.root_name = root_name
        self.binder = binder or FileSystemBinder()
        
        # State (initialized in bind)
        self.context: Optional[RootContext] = None
        self.rotation_config: Optional[LogRotationConfig] = None
        self.rotation_manager: Optional[RotationManager] = None
        self.logger: Optional[logging.Logger] = None
        self.current_log_file: Optional[Path] = None
        self.log_start_time: Optional[datetime] = None

        # Backwards compatibility properties (computed from context)
        # Accessing these before bind() will now fail or return None, which is cleaner than guessing.

    @property
    def root(self) -> Path:
        return self.context.root if self.context else Path(self.root_name)

    @property
    def app_root(self) -> Path:
        return self.context.app_root if self.context else self.root / self.config.name

    def bind(self, interactive_setup: bool = False):
        """Creates the structure and binds the logger."""
        
        # 1. Initialize Rotation Manager early to load config (needed for Binder)
        # We need a temporary location/logger to bootstrap rotation config logic
        # But wait, Binder needs rotation config to decide folder structure?
        # Yes, FileSystemBinder uses rotation_config.
        
        # Circular usage issue in legacy design: 
        # - RotationManager needs folders to exist to save config? Or just to load?
        # - It needs config_dir.
        
        # Solution: Two-phase binding or simplified pre-loading.
        # Let's resolve config layout first using a temp binder or manual check?
        
        # Clean approach:
        # 1. Binder calculates paths (stateless/pure where possible, or idempotent mkdir).
        # But we need RotationConfig to know relevant paths.
        
        # Pragmatic approach: 
        # Just instantiate RotationManager with calculated config path to load config.
        # Then pass that config to Binder.
        
        temp_root = Path(self.root_name)
        temp_config_dir = Path(self.config.config_dir) if self.config.config_dir else (temp_root / "config")
        temp_config_dir.mkdir(parents=True, exist_ok=True) # Minimal side effect required for config loading?
        
        # Temp Logger
        temp_logger = logging.getLogger(self.config.name)
        if not temp_logger.handlers:
            ch = logging.StreamHandler()
            ch.setFormatter(logging.Formatter('%(message)s'))
            temp_logger.addHandler(ch)
            temp_logger.setLevel(logging.INFO)

        self.rotation_manager = RotationManager(temp_config_dir, temp_root / self.config.name, temp_logger)
        self.rotation_config = self.rotation_manager.load_config()

        if not self.rotation_config:
            if interactive_setup:
                self.rotation_config = self.rotation_manager.prompt_and_cache_config()
            else:
                self.rotation_config = LogRotationConfig(enabled=False)
                self.rotation_manager.save_config(self.rotation_config)
        
        # Update Binder with loaded config if it's the default FileSystemBinder
        if isinstance(self.binder, FileSystemBinder):
            self.binder.rotation_config = self.rotation_config

        # 2. Bind (Create Directory Structure)
        self.context = self.binder.bind(self.config, self.root_name)
        
        # 3. Determine Initial Log File
        if self.rotation_config and self.rotation_config.enabled:
            timestamp = datetime.now().strftime(self.rotation_config.timestamp_format)
            log_file = self.context.log_base / self.rotation_config.log_data_dir / f"{timestamp}.log"
            self.current_log_file = log_file
            self.log_start_time = datetime.now()
            
            # Update rotation manager with real paths from context
            self.rotation_manager.current_log_file = self.current_log_file
            self.rotation_manager.log_start_time = self.log_start_time
            self.rotation_manager.app_root = self.context.log_base # Anchor rotation to log base
            
        else:
            log_file = self.context.log_base / "logs" / f"{self.config.name}.log"
            self.current_log_file = log_file

        # 4. Setup Logger
        self.logger = setup_logger(self.config.name, self.config.log_level, log_file)
        
        # 5. Connect Logger
        self.rotation_manager.logger = self.logger
        
        # 6. Capture Internal Logs
        internal_logger = logging.getLogger("nibandha")
        internal_logger.setLevel(self.config.log_level)
        for handler in self.logger.handlers:
            if handler not in internal_logger.handlers:
                internal_logger.addHandler(handler)
        internal_logger.propagate = False
        
        self.logger.info(f"Nibandha initialized at {self.context.app_root}")
        
        if self.rotation_config and self.rotation_config.enabled:
            self.logger.info(f"Log rotation enabled: {self.current_log_file.name}")
            self.rotation_manager.archive_old_logs_from_data()
            self.rotation_manager.cleanup_old_archives()

        return self

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

