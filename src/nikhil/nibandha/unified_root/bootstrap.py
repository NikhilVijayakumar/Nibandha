from pathlib import Path
from datetime import datetime
import logging
from typing import Optional, List, Tuple, TYPE_CHECKING
if TYPE_CHECKING:
    from nibandha.reporting import ReportGenerator

from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.configuration.domain.models.rotation_config import LogRotationConfig
from nibandha.logging.infrastructure.rotation_manager import RotationManager
from nibandha.logging.infrastructure.logger_factory import setup_logger

from nibandha.unified_root.domain.models.root_context import RootContext
from nibandha.unified_root.domain.protocols.root_binder import RootBinderProtocol
from nibandha.unified_root.infrastructure.filesystem_binder import FileSystemBinder
from nibandha.logging.application.logging_coordinator import LoggingCoordinator

class Nibandha:
    """
    Application Facade (Clean Architecture).
    Orchestrates the binding of configuration, filesystem, and logging.
    """

    def __init__(self, config: AppConfig, root_name: str = ".Nibandha", binder: Optional[RootBinderProtocol] = None):
        self.config = config
        self.root_name = root_name
        self.binder = binder or FileSystemBinder()
        
        self.logging_coordinator = LoggingCoordinator(config)
        self.context: Optional[RootContext] = None
        
    @property
    def root(self) -> Path:
        return self.context.root if self.context else Path(self.root_name)

    @property
    def app_root(self) -> Path:
        return self.context.app_root if self.context else self.root / self.config.name

    @property
    def config_dir(self) -> Path:
        if self.context:
            return self.context.config_dir
        # Default fallback logic matching bind()
        root = Path(self.root_name)
        return Path(self.config.config_dir) if self.config.config_dir else (root / "config")
        
    @property
    def log_base(self) -> Path:
        return self.context.log_base if self.context else (self.app_root / "logs")  # Fallback?

    # Delegated Properties for Backward Compatibility
    @property
    def logger(self) -> Optional[logging.Logger]:
        return self.logging_coordinator.logger

    @logger.setter
    def logger(self, value: Optional[logging.Logger]):
        self.logging_coordinator.logger = value

    @property
    def rotation_manager(self) -> Optional[RotationManager]:
        return self.logging_coordinator.rotation_manager

    @rotation_manager.setter
    def rotation_manager(self, value: Optional[RotationManager]):
        self.logging_coordinator.rotation_manager = value

    @property
    def rotation_config(self) -> Optional[LogRotationConfig]:
        return self.logging_coordinator.rotation_config

    @rotation_config.setter
    def rotation_config(self, value: Optional[LogRotationConfig]):
        self.logging_coordinator.rotation_config = value

    @property
    def current_log_file(self) -> Optional[Path]:
        return self.logging_coordinator.current_log_file

    @property
    def log_start_time(self) -> Optional[datetime]:
        return self.logging_coordinator.log_start_time

    def bind(self, interactive_setup: bool = False) -> "Nibandha":
        """Creates the structure and binds the logger."""
        
        # 1. Initialize Rotation Configuration (needed for Binder)
        temp_root = Path(self.root_name)
        temp_config_dir = Path(self.config.config_dir) if self.config.config_dir else (temp_root / "config")
        temp_config_dir.mkdir(parents=True, exist_ok=True) 

        rotation_config = self.logging_coordinator.initialize_rotation_manager(
            temp_config_dir, 
            temp_root / self.config.name, 
            interactive_setup
        )
        
        # Update Binder with loaded config if it's the default FileSystemBinder
        if isinstance(self.binder, FileSystemBinder):
            self.binder.rotation_config = rotation_config

        # 2. Bind (Create Directory Structure)
        self.context = self.binder.bind(self.config, self.root_name)
        
        # 3. Setup Logging with resolved context
        self.logging_coordinator.setup_logging(self.context)

        return self

    def should_rotate(self) -> bool:
        return self.logging_coordinator.should_rotate()

    def rotate_logs(self) -> None:
        self.logging_coordinator.rotate_logs()

    def cleanup_old_archives(self) -> int:
        return self.logging_coordinator.cleanup_old_archives()

    def generate_report(
        self,
        # Optional overrides (prefer config where possible)
        quality_target: Optional[str] = None,
        package_roots: Optional[List[str]] = None,
        unit_target: Optional[str] = None,
        e2e_target: Optional[str] = None,
        project_root: Optional[str] = None,
        export_formats: Optional[List[str]] = None
    ) -> Tuple[bool, List[str]]:
        """
        Generates all system reports using the configured context.
        Config prioritization: Arguments > AppConfig > Defaults
        
        Args:
            quality_target: Override quality metrics target.
            package_roots: Override package roots.
            unit_target: Override unit tests target.
            e2e_target: Override e2e tests target.
            project_root: Override project root.
            export_formats: Override export formats.
            
        Returns:
            Tuple[bool, List[str]]: (Success, Missing Artefacts List)
        """
        if not self.context:
            raise RuntimeError("Application must be bound before generating reports. Call .bind() first.")

        # Lazy imports
        from nibandha.configuration.domain.models.reporting_config import ReportingConfig
        from nibandha.reporting import ReportGenerator
        
        # Ensure proper Pydantic initialization
        try:
             ReportingConfig.model_rebuild()
        except ImportError:
             pass 

        # 1. Base Config from AppConfig (if valid)
        base_config = self.config.reporting
        
        # 2. Determine Defaults/Overrides
        # Project Root
        proj_root = Path(project_root) if project_root else self.app_root.parent
        
        # Output Directory (always derived from Context unless overridden? No, context is king)
        report_dir = self.context.app_root / "Report"
        docs_dir = proj_root / "docs"
        
        # 3. Construct Final ReportingConfig
        # We start with base_config values if present, else defaults
        
        # Helper to pick value: Arg > Config > Default
        def resolve(arg, config_attr, default):
            if arg is not None: return arg
            if base_config and getattr(base_config, config_attr, None) is not None:
                return getattr(base_config, config_attr)
            return default

        final_quality = resolve(quality_target, 'quality_target', "src")
        final_pkgs = resolve(package_roots, 'package_roots', [self.config.name.lower()])
        final_unit = resolve(unit_target, 'unit_target', "tests/unit")
        final_e2e = resolve(e2e_target, 'e2e_target', "tests/e2e")
        final_formats = resolve(export_formats, 'export_formats', ["md", "html"])
        
        # Explicit paths (Arguments can't easily override these complex objects via CLI-like args, so we trust config or context)
        # However, we must ensure output_dir and docs_dir are set for the Generator
        final_output = base_config.output_dir if (base_config and base_config.output_dir) else report_dir
        final_docs = base_config.docs_dir if (base_config and base_config.docs_dir) else docs_dir
        
        final_doc_paths = base_config.doc_paths if (base_config and base_config.doc_paths) else {
            "functional": Path("docs/features"), 
            "technical": Path("docs/technical"), 
            "test": Path("docs/test")
        }

        # Create Configuration Object
        config = ReportingConfig(
            output_dir=final_output,
            docs_dir=final_docs,
            export_formats=final_formats,
            project_name=self.config.name,
            quality_target=final_quality,
            package_roots=final_pkgs,
            unit_target=final_unit,
            e2e_target=final_e2e,
            doc_paths=final_doc_paths
        )
        
        # 4. Instantiate Generator
        generator = ReportGenerator(config=config)
        self.logger.info(f"Report Generation Initialized in: {generator.output_dir}")
        self.logger.info(f"Targets: Unit={final_unit}, E2E={final_e2e}, Quality={final_quality}")
        
        # 5. Generate
        # generator.generate_all now uses config mainly, but accepts overrides.
        # We pass overrides that are redundant but ensures generator uses what we resolved.
        generator.generate_all(
            unit_target=str(config.unit_target),
            e2e_target=str(config.e2e_target),
            quality_target=str(config.quality_target),
            project_root=str(proj_root)
        )
        
        # 6. Verify
        return generator.verify_generation()

