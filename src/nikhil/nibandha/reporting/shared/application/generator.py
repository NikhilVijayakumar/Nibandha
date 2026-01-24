import logging
import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Union
from ...unit.application import unit_reporter
from ...e2e.application import e2e_reporter
from ...quality.application import quality_reporter
from ...dependencies.application import dependency_reporter, package_reporter
from ..infrastructure import utils
from ..rendering.template_engine import TemplateEngine
from ..infrastructure.visualizers.default_visualizer import DefaultVisualizationProvider

from ..data.data_builders import SummaryDataBuilder

logger = logging.getLogger("nibandha.reporting")

from nibandha.configuration.domain.models.reporting_config import ReportingConfig
from nibandha.configuration.domain.models.app_config import AppConfig

class ReportGenerator:
    def __init__(
        self, 
        output_dir: Optional[str] = None,
        template_dir: Optional[str] = None,
        docs_dir: str = "docs/test",
        config: Optional[Union[AppConfig, ReportingConfig]] = None,
        visualization_provider: Optional[Any] = None
    ):
        """
        Initialize the ReportGenerator.
        
        Args:
            output_dir: Legacy. Directory where reports will be saved.
            template_dir: Legacy. Directory containing report templates.
            docs_dir: Legacy. Directory containing test scenarios.
            config: Optional AppConfig or ReportingConfig object (Preferred).
            visualization_provider: Optional custom visualization provider.
        """
        self.default_templates_dir = Path(__file__).parent.parent.parent / "templates"
        
        # 1. Resolve Configuration
        if config:
            if isinstance(config, AppConfig):
                # Map AppConfig to paths
                raw_out = config.report_dir or ".Nibandha/Report"
                self.output_dir = Path(raw_out).resolve()
                self.docs_dir = Path("docs/test").resolve() # AppConfig doesn't have docs_dir yet, verify?
                self.templates_dir = self.default_templates_dir
            elif isinstance(config, ReportingConfig):
                self.output_dir = config.output_dir
                self.docs_dir = config.docs_dir
                self.templates_dir = config.template_dir or self.default_templates_dir
        else:
            # Legacy / Manual Fallback
            out = output_dir or ".Nibandha/Report"
            self.output_dir = Path(out).resolve()
            self.docs_dir = Path(docs_dir).resolve()
            self.templates_dir = Path(template_dir).resolve() if template_dir else self.default_templates_dir

        # Store config and extract module discovery protocol
        self.config = config
        self.module_discovery = None
        if config and isinstance(config, ReportingConfig):
            self.module_discovery = config.module_discovery

        # 2. Setup Template Engine
        if self.templates_dir != self.default_templates_dir:
             self.template_engine = TemplateEngine(self.templates_dir, defaults_dir=self.default_templates_dir)
        else:
             self.template_engine = TemplateEngine(self.templates_dir)
        
        # Initialize Shared Services
        self.viz_provider = visualization_provider or DefaultVisualizationProvider()
        self.summary_builder = SummaryDataBuilder()
        
        # Determine source_root for module discovery
        # This should point to the package root where modules are located
        source_root = None
        if self.module_discovery:
            # If custom discovery is provided, we need a source root
            # Use a reasonable default or let reporters handle it
            source_root = Path.cwd() / "src"  # Default assumption
        
        # Initialize reporters with DI (including module discovery)
        self.unit_reporter = unit_reporter.UnitReporter(
            self.output_dir, self.templates_dir, self.docs_dir, 
            self.template_engine, self.viz_provider,
            self.module_discovery, source_root
        )
        self.e2e_reporter = e2e_reporter.E2EReporter(
            self.output_dir, self.templates_dir, self.docs_dir,
            self.template_engine, self.viz_provider,
            self.module_discovery, source_root
        )
        self.quality_reporter = quality_reporter.QualityReporter(
            self.output_dir, self.templates_dir,
            self.template_engine, self.viz_provider
        )
        self.dep_reporter = dependency_reporter.DependencyReporter(self.output_dir, self.templates_dir)
        self.dep_reporter = dependency_reporter.DependencyReporter(self.output_dir, self.templates_dir)
        self.pkg_reporter = package_reporter.PackageReporter(self.output_dir, self.templates_dir)
        
        # Initialize Export Service
        self.export_formats = ["md"]
        if config and isinstance(config, ReportingConfig):
            self.export_formats = config.export_formats
            
        self.export_service = None
        if "html" in self.export_formats or "docx" in self.export_formats:
             try:
                 from ...export import ExportService
                 self.export_service = ExportService()
             except ImportError as e:
                 logger.warning(f"Failed to import ExportService: {e}")
        
    def generate_all(self, 
                     unit_target: str = "tests/unit", 
                     e2e_target: str = "tests/e2e", 
                     package_target: str = "src/nikhil/nibandha",
                     project_root: str = None
                    ):
        """Run all tests and checks and generate reports."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Starting unified report generation at {timestamp}")
        
        if project_root:
            proj_path = Path(project_root)
        else:
            proj_path = Path.cwd()

        # Tests
        unit_data = self.run_unit_Tests(unit_target, timestamp)
        e2e_data = self.run_e2e_Tests(e2e_target, timestamp)
        
        # Quality
        quality_data = self.run_quality_checks(package_target)
        
        # Dependencies
        src_root = Path(package_target).resolve()
        dependency_data = self.run_dependency_checks(src_root, package_roots=["nikhil", "nibandha", "pravaha"])
        
        # Package Health
        package_data = self.run_package_checks(proj_path)
        
        # Documentation
        try:
             # run_documentation_checks is not fully implemented/integrated yet in this codebase version
             # but assuming it returns None or we skip it if not existent.
             # Based on previous file reads, it seemed missing or scaffolded.
             # Let's check if run_documentation_checks exists.
             # It was in the file content previously read: 
             # def run_documentation_checks(self, project_root: Path) -> Dict:
             documentation_data = self.run_documentation_checks(proj_path)
        except Exception as e:
             logger.warning(f"Documentation check validation failed/skipped: {e}")
             documentation_data = None
        
        # Generate Unified Summary
        summary_data = self.summary_builder.build(
            unit_data, 
            e2e_data, 
            quality_data,
            documentation_data=documentation_data,
            dependency_data=dependency_data,
            package_data=package_data
        )
        self.template_engine.render(
             "unified_overview_template.md",
             summary_data,
             self.output_dir / "summary.md"
        )
        logger.info(f"Generated unified summary at {self.output_dir / 'summary.md'}")
        
        # Export Reports
        self._export_reports()

        logger.info("Report generation complete.")
        
    def _export_reports(self):
        """Export all generated reports to configured formats."""
        if not self.export_service:
            return
            
        formats = [f for f in self.export_formats if f != "md"]
        if not formats:
            return
            
        logger.info(f"Exporting reports to: {formats}")
        
        # Export summary
        summary_path = self.output_dir / "summary.md"
        if summary_path.exists():
            self.export_service.export_document(summary_path, formats)
            
        # Export details
        details_dir = self.output_dir / "details"
        if details_dir.exists():
            for report in details_dir.glob("*.md"):
                self.export_service.export_document(report, formats)
        
    def run_unit_Tests(self, target: str, timestamp: str) -> Dict:
        """Run unit tests and generate report."""
        logger.info(f"Running unit tests on target: {target}")
        json_path = self.output_dir / "assets" / "data" / "unit.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Unit test JSON output: {json_path}")
        
        cov_target = "src/nikhil/nibandha" 
        
        utils.run_pytest(target, json_path, cov_target)
        
        data = utils.load_json(json_path)
        cov_data = utils.load_json(Path("coverage.json"))
        
        return self.unit_reporter.generate(data, cov_data, timestamp) or {}
        
    def run_e2e_Tests(self, target: str, timestamp: str) -> Dict:
        """Run E2E tests and generate report."""
        logger.info(f"Running E2E tests on target: {target}")
        json_path = self.output_dir / "assets" / "data" / "e2e.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug(f"E2E test JSON output: {json_path}")
        
        utils.run_pytest(target, json_path)
        data = utils.load_json(json_path)
        
        return self.e2e_reporter.generate(data, timestamp) or {}

    def run_quality_checks(self, target_package: str) -> Dict:
        """Run quality checks and generate report."""
        logger.info(f"Running quality checks on package: {target_package}")
        results = self.quality_reporter.run_checks(target_package)
        self.quality_reporter.generate(results)
        return results
        
        logger.info(f"Running dependency checks on source: {source_root}")
        self.dep_reporter.generate(source_root, package_roots)
        self.pkg_reporter.generate(project_root)

    def run_documentation_checks(self, project_root: Path) -> Dict:
        """Run documentation coverage checks."""
        logger.info(f"Running documentation checks on root: {project_root}")
        
        # Lazy init to avoid circular import or early init if not needed
        # But we need to init in __init__? The config has doc_paths.
        # Let's Init here or in __init__.
        # If I init in __init__, I need to update __init__ args to check config for doc_paths.
        
        # Check config
        doc_paths = {
            "functional": Path("docs/modules"), 
            "technical": Path("docs/technical"), 
            "test": Path("docs/test")
        }
        # If config is passed, try to get doc_paths (it's in ReportingConfig now)
        # But current `self.config` isn't stored, only `self.output_dir`.
        # I should have stored self.config.
        # Let's create the reporter here using default or config if accessible.
        
        from ...documentation.application import documentation_reporter
        
        # Determine source_root for module discovery
        source_root = None
        if self.module_discovery:
            source_root = Path.cwd() / "src"
        
        reporter = documentation_reporter.DocumentationReporter(
            self.output_dir, self.templates_dir, doc_paths,
            self.template_engine, self.viz_provider,
            self.module_discovery, source_root
        )
        data = reporter.generate(project_root)
        
        # Save JSON
        json_path = self.output_dir / "assets" / "data" / "documentation.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        import json
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Documentation data saved to {json_path}")
        
        return data

    def run_dependency_checks(self, source_root: Path, package_roots: list = None) -> Dict:
        """
        Run module dependency analysis.
        
        Args:
            source_root: Root directory of source code to analyze
            package_roots: Optional list of package names to analyze (e.g., ["nikhil.nibandha"])
            
        Returns:
            Dictionary with dependency analysis data
        """
        logger.info(f"Running dependency checks on source: {source_root}")
        
        reporter = dependency_reporter.DependencyReporter(self.output_dir, self.templates_dir)
        return reporter.generate(source_root, package_roots)

    def run_package_checks(self, project_root: Path) -> Dict:
        """
        Run package dependency analysis (PyPI packages, outdated deps, etc.).
        
        Args:
            project_root: Root directory of the project
            
        Returns:
            Dictionary with package analysis data
        """
        logger.info(f"Running package checks on project: {project_root}")
        
        reporter = package_reporter.PackageReporter(self.output_dir, self.templates_dir)
        return reporter.generate(project_root)
