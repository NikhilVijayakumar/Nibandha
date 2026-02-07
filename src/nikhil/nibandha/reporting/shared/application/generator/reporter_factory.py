import logging
from pathlib import Path
from typing import Any, Optional, Dict
from types import SimpleNamespace

# Core Services
from nibandha.reporting.shared.rendering.template_engine import TemplateEngine
from nibandha.reporting.shared.infrastructure.visualizers.default_visualizer import DefaultVisualizationProvider
from nibandha.reporting.shared.application.reference_collector import ReferenceCollector

# Reporters
from nibandha.reporting.unit.application import unit_reporter
from nibandha.reporting.e2e.application import e2e_reporter
from nibandha.reporting.quality.application import quality_reporter
from nibandha.reporting.dependencies.application import dependency_reporter, package_reporter
from nibandha.reporting.documentation.application import documentation_reporter
from nibandha.reporting.report_cover.application import cover_page_reporter
from nibandha.reporting.introduction.application import introduction_reporter

class ReporterInitializer:
    """Initializes shared services and reporters."""

    def __init__(self, default_templates_dir: Path):
        self.default_templates_dir = default_templates_dir

    def create_services(self, templates_dir: Path, visualization_provider: Optional[Any] = None) -> SimpleNamespace:
        services = SimpleNamespace()
        
        # Template Engine
        if templates_dir != self.default_templates_dir:
             services.template_engine = TemplateEngine(templates_dir, defaults_dir=self.default_templates_dir)
        else:
             services.template_engine = TemplateEngine(templates_dir)
             
        # Visualization
        services.viz_provider = visualization_provider or DefaultVisualizationProvider()
        
        # Reference Collector
        services.reference_collector = ReferenceCollector()
        
        return services

    def create_reporters(self, 
                         resolved_config: Any, 
                         services: Any, 
                         source_root: Path
                        ) -> SimpleNamespace:
        reporters = SimpleNamespace()
        
        reporters.cover_reporter = cover_page_reporter.CoverPageReporter(
            resolved_config.output_dir, resolved_config.templates_dir, services.template_engine
        )
        reporters.intro_reporter = introduction_reporter.IntroductionReporter(
            resolved_config.output_dir, resolved_config.templates_dir, services.template_engine
        )
        reporters.unit_reporter = unit_reporter.UnitReporter(
            resolved_config.output_dir, resolved_config.templates_dir, resolved_config.docs_dir, 
            services.template_engine, services.viz_provider,
            resolved_config.module_discovery, source_root, services.reference_collector
        )
        reporters.e2e_reporter = e2e_reporter.E2EReporter(
            resolved_config.output_dir, resolved_config.templates_dir, resolved_config.docs_dir,
            services.template_engine, services.viz_provider,
            resolved_config.module_discovery, source_root, services.reference_collector
        )
        reporters.quality_reporter = quality_reporter.QualityReporter(
            resolved_config.output_dir, resolved_config.templates_dir,
            services.template_engine, services.viz_provider,
            services.reference_collector, source_root=source_root
        )
        reporters.dep_reporter = dependency_reporter.DependencyReporter(
            resolved_config.output_dir, resolved_config.templates_dir,
            services.template_engine, services.viz_provider, services.reference_collector
        )
        reporters.pkg_reporter = package_reporter.PackageReporter(
            resolved_config.output_dir, resolved_config.templates_dir,
            services.template_engine, services.reference_collector
        )
        
        # Doc Reporter
        doc_paths = {
            "functional": Path("docs/features"), 
            "technical": Path("docs/technical"), 
            "test": Path("docs/test")
        }
        # Check config object directly if it has doc_paths (ReportingConfig)
        if hasattr(resolved_config.config, 'doc_paths') and resolved_config.config.doc_paths:
            doc_paths = resolved_config.config.doc_paths
            
        reporters.doc_reporter = documentation_reporter.DocumentationReporter(
            resolved_config.output_dir, resolved_config.templates_dir, doc_paths,
            services.template_engine, services.viz_provider,
            resolved_config.module_discovery, source_root, services.reference_collector
        )
        
        return reporters

    def create_export_service(self, config: Optional[Any]) -> Any:
        export_formats = ["md"]
        if hasattr(config, 'export_formats') and config.export_formats:
            export_formats = config.export_formats
            
        export_service = None
        if "html" in export_formats or "docx" in export_formats:
             try:
                 from nibandha.export import ExportService
                 export_service = ExportService()
             except Exception as e:
                 logging.getLogger("nibandha.reporting.generator").warning(f"Failed to init ExportService: {e}")
                 
        return export_service, export_formats
