from typing import Optional
from pathlib import Path
import tomli
from pydantic import BaseModel, Field, field_validator, model_validator

from nibandha.configuration.domain.models.logging_config import LoggingConfig
from nibandha.configuration.domain.models.reporting_config import ReportingConfig
from nibandha.configuration.domain.models.unified_root_config import UnifiedRootConfig
from nibandha.configuration.domain.models.export_config import ExportConfig

def _read_project_name_from_pyproject() -> str:
    """Read project name from pyproject.toml, fallback to 'Nibandha'."""
    try:
        pyproject_path = Path.cwd() / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                data = tomli.load(f)
                return data.get("project", {}).get("name", "Nibandha")
    except Exception:
        pass
    return "Nibandha"

class AppConfig(BaseModel):
    """
    Main Application Configuration.
    All fields are optional with sensible defaults.
    """
    # Optional name - defaults to pyproject.toml or 'Nibandha'
    name: str = Field(default_factory=_read_project_name_from_pyproject, description="Application Name")
    mode: str = Field(default="production", description="Operating Mode (dev/prod)")
    
    # Module Configurations - all optional with defaults
    logging: LoggingConfig = Field(default_factory=LoggingConfig, description="Logging Configuration")
    reporting: ReportingConfig = Field(default_factory=ReportingConfig, description="Reporting Configuration")
    unified_root: UnifiedRootConfig = Field(default_factory=UnifiedRootConfig, description="Unified Root Configuration")
    export: ExportConfig = Field(default_factory=ExportConfig, description="Export Configuration")

    @model_validator(mode='after')
    def resolve_paths(self) -> 'AppConfig':
        """
        Resolve default paths for logging and reporting based on Unified Root strategy.
        Prioritizes user-provided paths, falls back to structured defaults.
        """
        # 1. Ensure unified_root.name defaults to AppConfig.name (prefixed with dot if missing)
        app_name = self.name or "Nibandha"
        if self.unified_root.name is None:
            self.unified_root.name = str(Path(f".{app_name}"))
        
        root_name = self.unified_root.name
        root_path = Path(root_name)
        
        # 2. Determine Base Directory (Single vs Multi App Logic)
        # Check if root folder name matches app name (case-insensitive check for robustness)
        # e.g. .Nibandha (root) vs Nibandha (app) -> Single App Mode
        # e.g. .System (root) vs Pravaha (app) -> Multi App Mode
        
        is_single_app = root_name.lower().lstrip(".") == app_name.lower()
        
        if is_single_app:
            base_dir = root_path
        else:
            base_dir = root_path / app_name
            
        # 3. Resolve Logging Path
        # We need LoggingConfig to be mutable (default BaseModel is mutable)
        # If user hasn't customized log_dir (it defaults to "logs"), we repoint it to our unified structure
        # Use as_posix() to ensure forward slashes (cross-platform compatibility)
        if self.logging.log_dir == "logs":
            self.logging.log_dir = (base_dir / "logs").as_posix()

            
        # 4. Resolve Reporting Output Path
        if self.reporting.output_dir is None:
            self.reporting.output_dir = base_dir / "Report"
            
        # 5. Resolve Template Directory
        # Use explicit relative path for clarity and portability
        if self.reporting.template_dir is None:
            self.reporting.template_dir = Path("src/nikhil/nibandha/reporting/templates")
        
        # 5b. Resolve Export Styles Directory
        if self.export.styles_dir is None:
            self.export.styles_dir = Path("src/nikhil/nibandha/export/infrastructure/styles")
        
        # 5c. Resolve Export Template Directory
        if self.export.template_dir is None:
            self.export.template_dir = Path("src/nikhil/nibandha/export/infrastructure/templates")
        
        # 5d. Resolve Export Input Directory (Dynamic Default)
        if self.export.input_dir is None and self.reporting.output_dir:
            self.export.input_dir = self.reporting.output_dir / "details"

        # 5e. Resolve Export Output Directory
        if self.export.output_dir is None:
            # Use same directory as reporting output (Report) since exports are typically of reports
            if self.unified_root.name:
                base_dir = Path(self.unified_root.name)
                if self.name:
                    base_dir = base_dir / self.name
                self.export.output_dir = base_dir / "Report"
            else:
                self.export.output_dir = Path("exports")

        # 6. Sync Quality Target from pyproject.toml if default ("src")
        # If user hasn't customized quality_target (it defaults to "src"), try to sync with package-dir
        if self.reporting.quality_target == "src":
             try:
                 pyproject_path = Path.cwd() / "pyproject.toml"
                 if pyproject_path.exists():
                     with open(pyproject_path, "rb") as f:
                         data = tomli.load(f)
                         # Check tool.setuptools.package-dir
                         pkg_dir = data.get("tool", {}).get("setuptools", {}).get("package-dir", {})
                         # Look for root package map "" or "src" convention
                         root_pkg = pkg_dir.get("") or pkg_dir.get(".")
                         if root_pkg:
                             # Normalize to forward slashes for consistency
                             self.reporting.quality_target = root_pkg.replace("\\", "/")
             except Exception:
                 pass # robust fallback to "src"

        # 7. Sync Package Roots from pyproject.toml if empty
        # If user hasn't provided package_roots (defaults to []), infer from project name
        if not self.reporting.package_roots:
             try:
                 pyproject_path = Path.cwd() / "pyproject.toml"
                 if pyproject_path.exists():
                     with open(pyproject_path, "rb") as f:
                         data = tomli.load(f)
                         # Get project name and lowercase it (package names are usually lowercase)
                         project_name = data.get("project", {}).get("name", "")
                         if project_name:
                             self.reporting.package_roots = [project_name.lower()]
             except Exception:
                 pass # robust fallback to []

        return self
