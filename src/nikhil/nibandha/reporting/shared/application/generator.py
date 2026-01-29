
import logging
import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Union

from ...unit.application import unit_reporter
from ...e2e.application import e2e_reporter
from ...quality.application import quality_reporter
from ...dependencies.application import dependency_reporter, package_reporter
from ...documentation.application import documentation_reporter
from ...introduction.application import introduction_reporter

from ..infrastructure import utils
from ..rendering.template_engine import TemplateEngine
from ..infrastructure.visualizers.default_visualizer import DefaultVisualizationProvider
from .reference_collector import ReferenceCollector
from ..data.data_builders import SummaryDataBuilder

from nibandha.configuration.domain.models.reporting_config import ReportingConfig
from nibandha.configuration.domain.models.app_config import AppConfig

logger = logging.getLogger("nibandha.reporting")

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
        """
        self.default_templates_dir = Path(__file__).parent.parent.parent / "templates"
        
        # 1. Resolve Configuration
        self._resolve_configuration(config, output_dir, template_dir, docs_dir)

        # 2. Setup Template Engine
        self._setup_template_engine()
        
        # 3. Initialize Shared Services
        self.viz_provider = visualization_provider or DefaultVisualizationProvider()
        self.summary_builder = SummaryDataBuilder()
        self.reference_collector = ReferenceCollector()
        
        # 4. Determine Source Root
        source_root = self._determine_source_root()
        
        # 5. Initialize Reporters
        self._initialize_reporters(source_root)
        
        # 6. Initialize Export Service
        self._initialize_export_service(config)

    def _resolve_configuration(self, config, output_dir, template_dir, docs_dir):
        self.config = config
        self.module_discovery = None
        self.unit_target_default = "tests/unit"
        self.e2e_target_default = "tests/e2e"
        self.quality_target_default = "src"
        self.package_roots_default = None
        self.project_name = "Nibandha"
        
        if config:
            if isinstance(config, AppConfig):
                self._configure_from_app_config(config)
            elif isinstance(config, ReportingConfig):
                self._configure_from_reporting_config(config)
        else:
            out = output_dir or ".Nibandha/Report"
            self.output_dir = Path(out).resolve()
            self.docs_dir = Path(docs_dir).resolve()
            self.templates_dir = Path(template_dir).resolve() if template_dir else self.default_templates_dir

    def _configure_from_app_config(self, config):
        raw_out = config.report_dir or ".Nibandha/Report"
        self.output_dir = Path(raw_out).resolve()
        self.docs_dir = Path("docs/test").resolve()
        self.templates_dir = self.default_templates_dir
        self.project_name = config.name

    def _configure_from_reporting_config(self, config):
        self.output_dir = config.output_dir
        self.docs_dir = config.docs_dir
        self.templates_dir = config.template_dir or self.default_templates_dir
        self.module_discovery = config.module_discovery
        self.project_name = config.project_name
        self.quality_target_default = config.quality_target
        self.package_roots_default = config.package_roots if config.package_roots else None

    def _setup_template_engine(self):
        if self.templates_dir != self.default_templates_dir:
             self.template_engine = TemplateEngine(self.templates_dir, defaults_dir=self.default_templates_dir)
        else:
             self.template_engine = TemplateEngine(self.templates_dir)

    def _determine_source_root(self):
        if self.quality_target_default and self.quality_target_default != "src":
             return Path(self.quality_target_default).resolve()
        elif self.module_discovery:
             return Path.cwd() / "src"
        
        # Fallback to src, but attempt to drill down if nested namespaces exist
        base_src = Path.cwd() / "src"
        if base_src.exists():
             candidate = base_src / "nikhil" / "nibandha"
             if candidate.exists():
                 return candidate
        return base_src

    def _initialize_reporters(self, source_root):
        self.intro_reporter = introduction_reporter.IntroductionReporter(
            self.output_dir, self.templates_dir, self.template_engine
        )
        self.unit_reporter = unit_reporter.UnitReporter(
            self.output_dir, self.templates_dir, self.docs_dir, 
            self.template_engine, self.viz_provider,
            self.module_discovery, source_root, self.reference_collector
        )
        self.e2e_reporter = e2e_reporter.E2EReporter(
            self.output_dir, self.templates_dir, self.docs_dir,
            self.template_engine, self.viz_provider,
            self.module_discovery, source_root, self.reference_collector
        )
        self.quality_reporter = quality_reporter.QualityReporter(
            self.output_dir, self.templates_dir,
            self.template_engine, self.viz_provider,
            self.reference_collector, source_root=source_root
        )
        self.dep_reporter = dependency_reporter.DependencyReporter(
            self.output_dir, self.templates_dir,
            self.template_engine, self.reference_collector
        )
        self.pkg_reporter = package_reporter.PackageReporter(
            self.output_dir, self.templates_dir,
            self.template_engine, self.reference_collector
        )
        self._initialize_doc_reporter(source_root)

    def _initialize_doc_reporter(self, source_root):
        doc_paths = {
            "functional": Path("docs/modules"), 
            "technical": Path("docs/technical"), 
            "test": Path("docs/test")
        }
        if isinstance(self.config, ReportingConfig) and self.config.doc_paths:
            doc_paths = self.config.doc_paths
            
        self.doc_reporter = documentation_reporter.DocumentationReporter(
            self.output_dir, self.templates_dir, doc_paths,
            self.template_engine, self.viz_provider,
            self.module_discovery, source_root, self.reference_collector
        )

    def _initialize_export_service(self, config):
        self.export_formats = ["md"]
        if config and isinstance(config, ReportingConfig):
            self.export_formats = config.export_formats
            
        self.export_service = None
        if "html" in self.export_formats or "docx" in self.export_formats:
             try:
                 from ....export import ExportService
                 self.export_service = ExportService()
             except Exception as e:
                 logger.warning(f"Failed to init ExportService: {e}")

    def generate_all(self, 
                     unit_target: str = None, 
                     e2e_target: str = None, 
                     quality_target: str = None,
                     project_root: str = None
                    ):
        """Run all tests and checks and generate unified report."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Starting unified report generation at {timestamp}")
        
        if project_root:
            proj_path = Path(project_root)
        else:
            proj_path = Path.cwd()

        # Resolve Targets (Argument > Config/Default)
        u_target = unit_target or self.unit_target_default
        e_target = e2e_target or self.e2e_target_default
        q_target = quality_target or self.quality_target_default # Default set from config in init
        
        # 1. Introduction
        self.intro_reporter.generate(self.project_name)

        # 3. Unit Tests
        unit_data = self.run_unit_Tests(u_target, timestamp)
        
        # 4. E2E Tests
        e2e_data = self.run_e2e_Tests(e_target, timestamp)
        
        # 5,6,7. Quality Checks
        quality_data = self.run_quality_checks(q_target)
        
        # 8. Dependencies
        src_root = Path(q_target).resolve()
        # Use package_roots from config/default configured in init
        dependency_data = self.run_dependency_checks(src_root, self.package_roots_default)
        
        # 9. Package Health
        package_data = self.run_package_checks(proj_path)
        
        # 10. Documentation
        try:
             documentation_data = self.doc_reporter.generate(proj_path, project_name=self.project_name)
             # Save JSON
             json_path = self.output_dir / "assets" / "data" / "documentation.json"
             json_path.parent.mkdir(parents=True, exist_ok=True)
             import json
             with open(json_path, 'w') as f:
                 json.dump(documentation_data, f, indent=2, default=str)
        except Exception as e:
             logger.warning(f"Documentation check failed: {e}")
             documentation_data = None
        
        # 11. Conclusion (formerly Summary)
        summary_data = self.summary_builder.build(
            unit_data, 
            e2e_data, 
            quality_data,
            documentation_data=documentation_data,
            dependency_data=dependency_data,
            package_data=package_data
        )
        self.template_engine.render(
             "conclusion_template.md",
             summary_data,
             self.output_dir / "details" / "11_conclusion.md"
        )
        logger.info(f"Generated conclusion at {self.output_dir / 'details' / '11_conclusion.md'}")
        
        # Save summary data (used by export service header)
        summary_json_path = self.output_dir / "assets" / "data" / "summary_data.json"
        summary_json_path.parent.mkdir(parents=True, exist_ok=True)
        import json
        with open(summary_json_path, 'w') as f:
            json.dump(summary_data, f, indent=2, default=str)

        # 2. Global References (Generate NOW, after all data collected)
        self._generate_global_references(timestamp)
        
        # Export Unified Report
        self._export_reports()

        logger.info("Report generation complete.")
        
    def _export_reports(self):
        """Export all generated reports in strict order."""
        if not self.export_service:
            return
            
        formats = [f for f in self.export_formats if f != "md"]
        if not formats:
            return
            
        logger.info(f"Exporting reports to: {formats}")
        
        details_dir = self.output_dir / "details"
        
        # Strict Order of Importance
        ordered_files = [
            "01_introduction.md",               # 1
            "02_global_references.md",          # 2
            "03_unit_report.md",                # 3
            "04_e2e_report.md",                 # 4
            "05_architecture_report.md",        # 5
            "06_type_safety_report.md",         # 6
            "07_complexity_report.md",          # 7
            "08_module_dependency_report.md",   # 8
            "09_package_dependency_report.md",  # 9
            "10_documentation_report.md",       # 10
            "11_conclusion.md"                  # 11
        ]
        
        detail_paths = []
        if details_dir.exists():
            for name in ordered_files:
                path = details_dir / name
                if path.exists():
                    detail_paths.append(path)
        
        project_info = self._extract_project_info()
        dummy_summary = self.output_dir / "non_existent_summary.md"
        
        if detail_paths:
            self.export_service.export_unified_report(
                dummy_summary,
                detail_paths,
                self.output_dir,
                formats,
                project_info
            )
        
        self._cleanup_individual_exports()
    
    def _extract_project_info(self) -> dict:
        data_path = self.output_dir / "assets" / "data" / "summary_data.json"
        if data_path.exists():
            try:
                import json
                with open(data_path) as f:
                    data = json.load(f)
                return {
                    "name": self.project_name or "Nibandha Quality Report",
                    "grade": data.get("display_grade", "F"),
                    "status": data.get("overall_status", "Unknown")
                }
            except Exception as e:
                logger.warning(f"Failed to load summary data: {e}")
        return {"name": self.project_name, "grade": "N/A", "status": "Complete"}
    
    def _cleanup_individual_exports(self):
        logger.info("Cleaning up output dir exports...")
        pass 

    def _generate_global_references(self, timestamp: str):
        logger.info("Generating global references document")
        references = self.reference_collector.get_all_references()
        data = {
            "date": timestamp,
            "figures": [fig.model_dump() for fig in references.figures],
            "tables": [tab.model_dump() for tab in references.tables],
            "nomenclature": [nom.model_dump() for nom in references.nomenclature],
            "project_name": self.project_name
        }
        output_path = self.output_dir / "details" / "02_global_references.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.template_engine.render("global_references_template.md", data, output_path)
        
    def run_unit_Tests(self, target: str, timestamp: str) -> Dict:
        logger.info(f"Running unit tests on target: {target}")
        json_path = self.output_dir / "assets" / "data" / "unit.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        
        cov_target = "src/nikhil/nibandha"
        if self.config and isinstance(self.config, ReportingConfig):
            # If we want coverage target to be configurable, add to ReportingConfig. 
            # For now default to package root.
            # Assuming 'target' passed to unit_Tests encapsulates what to test.
            # Coverage usually needs source root.
            pass

        utils.run_pytest(target, json_path, cov_target)
        
        data = utils.load_json(json_path)
        cov_data = utils.load_json(Path("coverage.json"))
        return self.unit_reporter.generate(data, cov_data, timestamp, project_name=self.project_name) or {}
        
    def run_e2e_Tests(self, target: str, timestamp: str) -> Dict:
        logger.info(f"Running E2E tests on target: {target}")
        json_path = self.output_dir / "assets" / "data" / "e2e.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        
        utils.run_pytest(target, json_path)
        data = utils.load_json(json_path)
        return self.e2e_reporter.generate(data, timestamp, project_name=self.project_name) or {}

    def run_quality_checks(self, target_package: str) -> Dict:
        logger.info(f"Running quality checks on package: {target_package}")
        results = self.quality_reporter.run_checks(target_package)
        self.quality_reporter.generate(results, project_name=self.project_name)
        return results

    def run_dependency_checks(self, source_root: Path, package_roots: list = None) -> Dict:
        logger.info(f"Running dependency checks on source: {source_root}")
        return self.dep_reporter.generate(source_root, package_roots, project_name=self.project_name)

    def run_package_checks(self, project_root: Path) -> Dict:
        logger.info(f"Running package checks on project: {project_root}")
        return self.pkg_reporter.generate(project_root, project_name=self.project_name)
