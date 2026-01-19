import logging
import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from ...unit.application import unit_reporter
from ...e2e.application import e2e_reporter
from ...quality.application import quality_reporter
from ...dependencies.application import dependency_reporter, package_reporter
from ..infrastructure import utils
from ..rendering.template_engine import TemplateEngine
from ..infrastructure.visualizers.default_visualizer import DefaultVisualizationProvider

from ..data.data_builders import SummaryDataBuilder

logger = logging.getLogger("nibandha.reporting")

class ReportGenerator:
    def __init__(
        self, 
        output_dir: str = ".Nibandha/Report",
        template_dir: Optional[str] = None,
        docs_dir: str = "docs/test",
        visualization_provider: Optional[Any] = None
    ):
        """
        Initialize the ReportGenerator.
        
        Args:
            output_dir: Directory where reports will be saved.
            template_dir: Directory containing report templates. Falls back to package defaults.
            docs_dir: Directory containing test documentation scenarios.
            visualization_provider: Optional custom visualization provider.
        """
        self.output_dir = Path(output_dir).resolve()
        
        self.default_templates_dir = Path(__file__).parent.parent.parent / "templates"
        
        if template_dir:
            self.templates_dir = Path(template_dir).resolve()
            # If user provides custom dir, we use default as fallback
            self.template_engine = TemplateEngine(self.templates_dir, defaults_dir=self.default_templates_dir)
        else:
            self.templates_dir = self.default_templates_dir
            self.template_engine = TemplateEngine(self.templates_dir)
            
        self.docs_dir = Path(docs_dir).resolve()
        
        # Initialize Shared Services
        self.viz_provider = visualization_provider or DefaultVisualizationProvider()
        self.summary_builder = SummaryDataBuilder()
        
        # Initialize reporters with DI
        self.unit_reporter = unit_reporter.UnitReporter(
            self.output_dir, self.templates_dir, self.docs_dir, 
            self.template_engine, self.viz_provider
        )
        self.e2e_reporter = e2e_reporter.E2EReporter(
            self.output_dir, self.templates_dir, self.docs_dir,
            self.template_engine, self.viz_provider
        )
        self.quality_reporter = quality_reporter.QualityReporter(
            self.output_dir, self.templates_dir,
            self.template_engine, self.viz_provider
        )
        self.dep_reporter = dependency_reporter.DependencyReporter(self.output_dir, self.templates_dir)
        self.pkg_reporter = package_reporter.PackageReporter(self.output_dir, self.templates_dir)
        
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
        self.run_dependency_checks(src_root, proj_path, package_roots=["nikhil", "nibandha", "pravaha"])
        
        # Generate Unified Summary
        summary_data = self.summary_builder.build(unit_data, e2e_data, quality_data)
        self.template_engine.render(
             "unified_overview_template.md",
             summary_data,
             self.output_dir / "summary.md"
        )
        logger.info(f"Generated unified summary at {self.output_dir / 'summary.md'}")

        logger.info("Report generation complete.")
        
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
        
    def run_dependency_checks(self, source_root: Path, project_root: Path, package_roots: list):
        """Run dependency modules."""
        logger.info(f"Running dependency checks on source: {source_root}")
        self.dep_reporter.generate(source_root, package_roots)
        self.pkg_reporter.generate(project_root)
