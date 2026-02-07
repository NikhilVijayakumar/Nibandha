import logging
import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Union, List, Tuple

# Core
from nibandha.reporting.shared.infrastructure import utils
from nibandha.configuration.domain.models.reporting_config import ReportingConfig
from nibandha.configuration.domain.models.app_config import AppConfig

# Orchestration
from nibandha.reporting.shared.application.orchestration.context import ReportingContext
from nibandha.reporting.shared.application.orchestration.orchestrator import ReportingOrchestrator
from nibandha.reporting.shared.application.orchestration.steps import (
    CoverPageStep, IntroductionStep, UnitTestStep, E2ETestStep,
    QualityCheckStep, DependencyCheckStep, PackageHealthStep,
    DocumentationStep, ConclusionStep, GlobalReferencesStep, ExportStep
)

# Factories
from .configuration_factory import ConfigurationResolver
from .reporter_factory import ReporterInitializer

logger = logging.getLogger("nibandha.reporting")

class ReportGenerator:
    """
    Main entry point for report generation.
    Refactored to use an Orchestrator pattern with discrete steps and package-based structure.
    """
    def __init__(
        self, 
        output_dir: Optional[str] = None,
        template_dir: Optional[str] = None,
        docs_dir: str = "docs/test",
        config: Optional[Union[AppConfig, ReportingConfig]] = None,
        visualization_provider: Optional[Any] = None
    ):
        self.default_templates_dir = Path(__file__).parent.parent.parent.parent / "templates"
        
        # 1. Resolve Configuration
        resolver = ConfigurationResolver(self.default_templates_dir)
        self.resolved_config = resolver.resolve(config, output_dir, template_dir, docs_dir)
        
        # Expose attributes for backward compatibility
        self.output_dir = self.resolved_config.output_dir
        self.project_name = self.resolved_config.project_name
        self.templates_dir = self.resolved_config.templates_dir
        self.docs_dir = self.resolved_config.docs_dir
        self.config = self.resolved_config.config
        self.module_discovery = self.resolved_config.module_discovery
        self.unit_target_default = self.resolved_config.unit_target_default
        self.e2e_target_default = self.resolved_config.e2e_target_default
        self.quality_target_default = self.resolved_config.quality_target_default
        self.package_roots_default = self.resolved_config.package_roots_default

        # 2. Determine Source Root
        self.source_root = resolver.determine_source_root(self.resolved_config)

        # 3. Initialize Shared Services & Reporters
        initializer = ReporterInitializer(self.default_templates_dir)
        self.services = initializer.create_services(self.templates_dir, visualization_provider)
        
        # Expose services
        self.template_engine = self.services.template_engine
        self.viz_provider = self.services.viz_provider
        self.reference_collector = self.services.reference_collector
        
        self.reporters = initializer.create_reporters(self.resolved_config, self.services, self.source_root)
        
        # Expose reporters for legacy access & steps
        self.cover_reporter = self.reporters.cover_reporter
        self.intro_reporter = self.reporters.intro_reporter
        self.unit_reporter = self.reporters.unit_reporter
        self.e2e_reporter = self.reporters.e2e_reporter
        self.quality_reporter = self.reporters.quality_reporter
        self.dep_reporter = self.reporters.dep_reporter
        self.pkg_reporter = self.reporters.pkg_reporter
        self.doc_reporter = self.reporters.doc_reporter

        # 4. Initialize Export Service
        self.export_service, self.export_formats = initializer.create_export_service(self.config)

    def generate_all(self, 
                     unit_target: Optional[str] = None, 
                     e2e_target: Optional[str] = None, 
                     quality_target: Optional[str] = None,
                     project_root: Optional[str] = None
                    ) -> None:
        """Run all tests and checks and generate unified report using Orchestrator."""
        
        # 1. Prepare Context
        context = ReportingContext(
            output_dir=self.output_dir,
            templates_dir=self.templates_dir,
            docs_dir=self.docs_dir,
            project_name=self.project_name,
            template_engine=self.template_engine,
            viz_provider=self.viz_provider,
            reference_collector=self.reference_collector,
            config=self.config,
            module_discovery=self.module_discovery,
            source_root=self.source_root,
            export_service=self.export_service,
            export_formats=self.export_formats,
            unit_target=unit_target or self.unit_target_default,
            e2e_target=e2e_target or self.e2e_target_default,
            quality_target=quality_target or self.quality_target_default
        )
        
        # Resolve Targets
        u_target = unit_target or self.unit_target_default
        e_target = e2e_target or self.e2e_target_default
        q_target = quality_target or self.quality_target_default
        
        # 2. Define Steps
        steps = [
            CoverPageStep(self.cover_reporter),
            IntroductionStep(self.intro_reporter),
            UnitTestStep(self.unit_reporter, u_target),
            E2ETestStep(self.e2e_reporter, e_target),
            QualityCheckStep(self.quality_reporter, q_target),
            DependencyCheckStep(
                self.dep_reporter, 
                Path(q_target).resolve(), 
                self.package_roots_default
            ),
            PackageHealthStep(self.pkg_reporter, Path(project_root or Path.cwd())),
            DocumentationStep(self.doc_reporter, Path(project_root or Path.cwd())),
            ConclusionStep(),
            GlobalReferencesStep(),
            ExportStep()
        ]
        
        # 3. Create and Run Orchestrator
        orchestrator = ReportingOrchestrator(context, steps)
        orchestrator.run()

    def verify_generation(self) -> Tuple[bool, List[str]]:
        """
        Verifies that all expected report artifacts have been generated.
        Returns (True, []) if all exist, else (False, [missing_files]).
        """
        expected_details = [
            "00_cover_page.md",
            "01_introduction.md",
            "03_unit_report.md",
            "04_e2e_report.md",
            "05_architecture_report.md",
            "06_type_safety_report.md",
            "07_complexity_report.md",
            "08_code_hygiene_report.md",
            "09_duplication_report.md",
            "10_security_report.md",
            "11_module_dependency_report.md",
            "12_package_dependency_report.md",
            "13_documentation_report.md",
            "14_encoding_report.md",
            "15_conclusion.md"
        ]
        
        missing = []
        details_dir = self.output_dir / "details"
        
        for filename in expected_details:
            if not (details_dir / filename).exists():
                missing.append(f"details/{filename}")
                
        # Also check for the unified report if export was requested (default is md)
        # Assuming unified report is always generated? 
        # The orchestrator logic suggests 'ExportStep' handles this.
        # Usually it's in output_dir / "unified_report.md" or similar. 
        # But looking at previous verify_system, it didn't check for unified.
        # Let's stick to checking detailed reports as they are the source of truth for "15 reports".
        
        return (len(missing) == 0, missing)

    # Legacy methods removed for clean implementation

            

