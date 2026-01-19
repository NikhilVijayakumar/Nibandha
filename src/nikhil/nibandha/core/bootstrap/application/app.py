from pathlib import Path
from datetime import datetime
import logging
from typing import Optional

from ...configuration.domain.config import AppConfig
from ...rotation.domain.config import LogRotationConfig
from ...rotation.infrastructure.manager import RotationManager
from ...logging.infrastructure.setup import setup_logger

class Nibandha:
    def __init__(self, config: AppConfig, root_name: str = ".Nibandha"):
        self.config = config
        self.root = Path(root_name)
        self.app_root = self.root / config.name
        
        # Path Resolution
        self.config_dir = Path(config.config_dir) if config.config_dir else (self.root / "config")
        self.report_dir = Path(config.report_dir) if config.report_dir else (self.app_root / "Report")
        
        # Log base determination (used in bind)
        self._log_base = Path(config.log_dir) if config.log_dir else self.app_root
        
        # State
        self.rotation_config: Optional[LogRotationConfig] = None
        self.rotation_manager: Optional[RotationManager] = None
        self.logger: Optional[logging.Logger] = None
        self.current_log_file: Optional[Path] = None
        self.log_start_time: Optional[datetime] = None

    def bind(self, interactive_setup: bool = False):
        """Creates the structure and binds the logger."""
        # Create config directory first
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Rotation Manager (Temporary logger until setup)
        temp_logger = logging.getLogger(self.config.name) 
        
        # Bootstrap logger for interactive wizard if needed
        if not temp_logger.handlers:
            ch = logging.StreamHandler()
            ch.setFormatter(logging.Formatter('%(message)s'))
            temp_logger.addHandler(ch)
            temp_logger.setLevel(logging.INFO)

        self.rotation_manager = RotationManager(self.config_dir, self.app_root, temp_logger)
        
        self.rotation_config = self.rotation_manager.load_config()
        if not self.rotation_config:
            if interactive_setup:
                self.rotation_config = self.rotation_manager.prompt_and_cache_config()
            else:
                # Default to disabled in non-interactive mode
                self.rotation_config = LogRotationConfig(enabled=False)
                # Ideally we save this default so we don't check every time, or we leave it missing?
                # User preference: "everything from configuration". Creating a file makes it explicit.
                self.rotation_manager.save_config(self.rotation_config)
        
        # 2. Create directory structure
        # 2. Create directory structure
        # If custom log dir, we use that as base for rotation folders
        # But we must respect that rotation config might check specific paths.
        
        if self.rotation_config and self.rotation_config.enabled:
            # Anchor rotation dirs to _log_base
            # If _log_base matches app_root, behaviors is default.
            # If overridden, ensures logs go there.
            
            # Note: config.log_data_dir is usually "logs/data". 
            # If log_dir override is provided (e.g. "C:/Logs"), we get "C:/Logs/logs/data".
            # This is acceptable to ensuring structure.
            
            folders_to_create = []
            folders_to_create.append(self._log_base / self.rotation_config.log_data_dir)
            folders_to_create.append(self._log_base / self.rotation_config.archive_dir)
            
            # Custom folders still go to App Root? 
            # "custom_folders" in AppConfig usually meant app structure.
            # Let's keep custom folders in app_root.
            for cf in self.config.custom_folders:
                folders_to_create.append(self.app_root / cf)
                
        else:
            # Legacy: Create 'logs' dir in _log_base
            folders_to_create = [self._log_base / "logs"]
            for cf in self.config.custom_folders:
                folders_to_create.append(self.app_root / cf)
        
        for folder in folders_to_create:
            folder.mkdir(parents=True, exist_ok=True)
            
        # 3. Determine Initial Log File
        if self.rotation_config and self.rotation_config.enabled:
            timestamp = datetime.now().strftime(self.rotation_config.timestamp_format)
            log_file = self._log_base / self.rotation_config.log_data_dir / f"{timestamp}.log"
            self.current_log_file = log_file
            self.log_start_time = datetime.now()
            
            # Update manager state
            self.rotation_manager.current_log_file = self.current_log_file
            self.rotation_manager.log_start_time = self.log_start_time
            # Update manager app_root to point to _log_base so it rotates correctly?
            # RotationManager uses self.app_root to resolve paths. 
            # We initialized RM with self.app_root in __init__ (via bind line 40).
            # We MUST update RM's app_root to _log_base if we want it to find the files there.
            self.rotation_manager.app_root = self._log_base
            
        else:
            # Legacy: If log_dir is custom, maybe filename changes?
            # User said "filename could be better with data than app name".
            # "Data" -> Date?
            # We can try to incorporate date if requested?
            # But stick to spec: app name log in logs dir.
            log_file = self._log_base / "logs" / f"{self.config.name}.log"
            self.current_log_file = log_file

        # 4. Setup Logger
        self.logger = setup_logger(self.config.name, self.config.log_level, log_file)
        
        # 5. Update Manager with Real Logger
        self.rotation_manager.logger = self.logger
        
        # 6. Capture Nibandha Library Logs
        # Ensure that logs from internal modules ('nibandha.*') appear in the app log
        internal_logger = logging.getLogger("nibandha")
        internal_logger.setLevel(self.config.log_level)
        for handler in self.logger.handlers:
            if handler not in internal_logger.handlers:
                internal_logger.addHandler(handler)
        
        # Do not propagate nibandha logs to root if we handle them here
        internal_logger.propagate = False
        
        self.logger.info(f"Nibandha initialized at {self.app_root}")
        
        if self.rotation_config and self.rotation_config.enabled:
            self.logger.info(f"Log rotation enabled: {self.current_log_file.name}")

        return self

    def should_rotate(self) -> bool:
        """Check if rotation is needed."""
        if not self.rotation_manager:
            return False
        return self.rotation_manager.should_rotate()

    def rotate_logs(self) -> None:
        """Manually trigger log rotation."""
        if self.rotation_manager:
            self.rotation_manager.rotate_logs()
            # Update local state from manager if needed
            self.current_log_file = self.rotation_manager.current_log_file
            self.log_start_time = self.rotation_manager.log_start_time

    def cleanup_old_archives(self) -> int:
        """Delete old archives."""
        if not self.rotation_manager:
            return 0
        return self.rotation_manager.cleanup_old_archives()
