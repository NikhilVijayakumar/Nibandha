from pathlib import Path
from typing import List, Optional
from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.configuration.domain.models.rotation_config import LogRotationConfig
from nibandha.unified_root.domain.models.root_context import RootContext
from nibandha.unified_root.domain.protocols.root_binder import RootBinderProtocol

class FileSystemBinder:
    """
    Standard implementation of RootBinderProtocol that works on the real filesystem.
    """
    def __init__(self, rotation_config: Optional[LogRotationConfig] = None):
        self.rotation_config = rotation_config

    def _get_project_name_from_toml(self) -> str:
        """Attempts to read the project name from pyproject.toml in the current working directory."""
        try:
            import toml
            if Path("pyproject.toml").exists():
                data = toml.load("pyproject.toml")
                # Try poetry format
                if "tool" in data and "poetry" in data["tool"]:
                    return data["tool"]["poetry"]["name"]
                # Try standard project format
                if "project" in data:
                    return data["project"]["name"]
        except Exception:
            pass # Fallback if toml library missing or file error
        return "Nibandha" # Default fallback

    def _create_custom_structure(self, base_path: Path, structure: dict):
        """Recursively creates custom folder structure."""
        for name, content in structure.items():
            current_path = base_path / name
            current_path.mkdir(parents=True, exist_ok=True)
            if isinstance(content, dict):
                self._create_custom_structure(current_path, content)

    def bind(self, config: AppConfig, root_name: str = ".Nibandha") -> RootContext:
        # Resolve Root Name
        resolved_root_name = root_name
        
        # Priority 1: explicitly passed root_name (legacy compat or override)
        # Priority 2: config.unified_root.name
        # Priority 3: pyproject.toml name (prefixed with .)
        # Priority 4: Default ".Nibandha"
        
        if config.unified_root and config.unified_root.name:
            resolved_root_name = config.unified_root.name
        elif root_name == ".Nibandha": # Only override if it's the default
            project_name = self._get_project_name_from_toml()
            resolved_root_name = f".{project_name}"

        root = Path(resolved_root_name)
        app_root = root / config.name
        
        # Determine Single/Multi App Mode
        # Same logic as AppConfig.resolve_paths
        is_single_app = resolved_root_name.lower().lstrip(".") == config.name.lower()

        if is_single_app:
            base_dir = root
        else:
            base_dir = app_root
        
        # Path Resolution from Config or Defaults
        # Config dir should be namespaced to the App (base_dir), not shared at Root
        config_dir = base_dir / "config"
        report_dir = config.reporting.output_dir if config.reporting.output_dir else (base_dir / "Report")
        log_base = Path(config.logging.log_dir) if config.logging.log_dir else base_dir
        
        # Prepare context
        context = RootContext(
            root=root,
            app_root=app_root,
            config_dir=config_dir,
            report_dir=report_dir,
            log_base=log_base
        )
        
        # Calculate folders to create
        folders_to_create: List[Optional[Path]] = [
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
             
        # Create standard directories
        for folder in folders_to_create:
            if folder:
                folder.mkdir(parents=True, exist_ok=True)

        # Custom Structure from unified_root config
        if config.unified_root and config.unified_root.custom_structure:
            self._create_custom_structure(context.root, config.unified_root.custom_structure)

        return context
