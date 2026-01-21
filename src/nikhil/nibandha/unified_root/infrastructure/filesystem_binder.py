from pathlib import Path
from typing import List
from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.logging.domain.models.rotation_config import LogRotationConfig
from ..domain.models.root_context import RootContext
from ..domain.protocols.root_binder import RootBinderProtocol

class FileSystemBinder:
    """
    Standard implementation of RootBinderProtocol that works on the real filesystem.
    """
    def __init__(self, rotation_config: LogRotationConfig = None):
        self.rotation_config = rotation_config

    def bind(self, config: AppConfig, root_name: str = ".Nibandha") -> RootContext:
        root = Path(root_name)
        app_root = root / config.name
        
        # Path Resolution from Config or Defaults
        config_dir = Path(config.config_dir) if config.config_dir else (root / "config")
        report_dir = Path(config.report_dir) if config.report_dir else (app_root / "Report")
        log_base = Path(config.log_dir) if config.log_dir else app_root
        
        # Prepare context
        context = RootContext(
            root=root,
            app_root=app_root,
            config_dir=config_dir,
            report_dir=report_dir,
            log_base=log_base
        )
        
        # Calculate folders to create
        folders_to_create: List[Path] = [
            context.config_dir,
            context.report_dir, # Note: Pydantic models use dot notation usually, but keeping simple
            context.log_base if not self.rotation_config else None
        ]

        # Use dot notation as standard pydantic access
        folders_to_create = [
            context.config_dir,
            context.report_dir
        ]

        if self.rotation_config and self.rotation_config.enabled:
             # Anchor rotation dirs to log_base
             folders_to_create.append(context.log_base / self.rotation_config.log_data_dir)
             folders_to_create.append(context.log_base / self.rotation_config.archive_dir)
        else:
             # Legacy logs folder
             folders_to_create.append(context.log_base / "logs")
             
        # Custom Folders (always relative to app_root)
        for cf in config.custom_folders:
            folders_to_create.append(context.app_root / cf)
            
        # Create directories
        for folder in folders_to_create:
            if folder:
                folder.mkdir(parents=True, exist_ok=True)
                
        return context
