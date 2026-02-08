import logging
from pathlib import Path
from types import SimpleNamespace
from typing import Optional, Union, Any

from nibandha.configuration.domain.models.reporting_config import ReportingConfig
from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.reporting.shared.constants import (
    DEFAULT_UNIT_TESTS_DIR,
    DEFAULT_E2E_TESTS_DIR,
    DEFAULT_SOURCE_ROOT
)

logger = logging.getLogger("nibandha.reporting.generator.config")

class ConfigurationResolver:
    """Resolves configuration and paths for the ReportGenerator."""
    
    def __init__(self, default_templates_dir: Path):
        self.default_templates_dir = default_templates_dir

    def resolve(self, 
                config: Optional[Union[AppConfig, ReportingConfig]], 
                output_dir: Optional[str], 
                template_dir: Optional[str], 
                docs_dir: str
               ) -> Any:
        """
        Resolves configuration into a standardized object.
        Returns a SimpleNamespace with attributes expected by the generator.
        """
        resolved = SimpleNamespace()
        resolved.config = config
        resolved.module_discovery = None
        resolved.unit_target_default = DEFAULT_UNIT_TESTS_DIR
        resolved.e2e_target_default = DEFAULT_E2E_TESTS_DIR
        resolved.quality_target_default = DEFAULT_SOURCE_ROOT
        resolved.package_roots_default = None
        resolved.project_name = "Nibandha"
        
        # Initialize defaults from arguments first (fallback)
        out = output_dir or ".Nibandha/Report"
        resolved.output_dir = Path(out).resolve()
        resolved.docs_dir = Path(docs_dir).resolve()
        resolved.templates_dir = Path(template_dir).resolve() if template_dir else self.default_templates_dir
        
        if config:
            if isinstance(config, AppConfig):
                self._configure_from_app_config(config, resolved)
            elif isinstance(config, ReportingConfig):
                self._configure_from_reporting_config(config, resolved)
            else:
                logger.warning(f"Unknown config type: {type(config)}. Using default/argument configuration.")
            
        return resolved

    def _configure_from_app_config(self, config: "AppConfig", resolved: Any) -> None:
        # Delegate to reporting config logic
        self._configure_from_reporting_config(config.reporting, resolved)
        # Override project name if present in AppConfig
        if config.name:
            resolved.project_name = config.name

    def _configure_from_reporting_config(self, config: "ReportingConfig", resolved: Any) -> None:
        resolved.output_dir = config.output_dir
        resolved.docs_dir = config.docs_dir
        resolved.templates_dir = config.template_dir or self.default_templates_dir
        
        # Handle Module Discovery (Static List vs Protocol)
        if isinstance(config.module_discovery, list):
             from nibandha.reporting.shared.infrastructure.static_module_discovery import StaticModuleDiscovery
             resolved.module_discovery = StaticModuleDiscovery(config.module_discovery)
        else:
             resolved.module_discovery = config.module_discovery # type: ignore
             
        # Use ReportingConfig.project_name if AppConfig didn't set it (logic order matters)
        # But AppConfig delegate calls this first, so AppConfig name overrides correctly if we set it AFTER.
        # Wait, if AppConfig sets it after, then ReportingConfig settings here are fine.
        if hasattr(config, "project_name") and config.project_name != "Nibandha": # Specific check?
             resolved.project_name = config.project_name
             
        resolved.quality_target_default = config.quality_target
        resolved.package_roots_default = config.package_roots if config.package_roots else None # type: ignore

    def determine_source_root(self, resolved_config: Any) -> Path:
        if resolved_config.quality_target_default and resolved_config.quality_target_default != "src":
             return Path(resolved_config.quality_target_default).resolve()
        elif resolved_config.module_discovery:
             return Path.cwd() / "src"
        
        # Fallback
        base_src = Path.cwd() / "src"
        if base_src.exists():
             candidate = base_src / "nikhil" / "nibandha"
             if candidate.exists():
                 return candidate
        return base_src
