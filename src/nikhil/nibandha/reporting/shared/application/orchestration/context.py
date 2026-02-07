from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import time

from nibandha.reporting.shared.domain.protocols.template_provider_protocol import TemplateProviderProtocol
from nibandha.reporting.shared.domain.protocols.visualization_protocol import VisualizationProvider
from nibandha.reporting.shared.domain.protocols.reference_collector_protocol import ReferenceCollectorProtocol
from nibandha.reporting.shared.data.data_builders import SummaryDataBuilder
from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.configuration.domain.models.reporting_config import ReportingConfig

class ReportingContext:
    def __init__(
        self,
        output_dir: Path,
        templates_dir: Path,
        docs_dir: Path,
        project_name: str,
        template_engine: TemplateProviderProtocol,
        viz_provider: VisualizationProvider,
        reference_collector: ReferenceCollectorProtocol,
        config: Optional[Union[AppConfig, ReportingConfig]] = None,
        module_discovery: Optional[Any] = None,
        source_root: Optional[Path] = None,
        export_service: Optional[Any] = None,
        force_export: bool = False,
        export_formats: Optional[List[str]] = None,

        unit_target: Optional[str] = None,
        e2e_target: Optional[str] = None,
        quality_target: Optional[str] = None
    ):
        self.output_dir = output_dir
        self.templates_dir = templates_dir
        self.docs_dir = docs_dir
        self.project_name = project_name
        self.template_engine = template_engine
        self.viz_provider = viz_provider
        self.reference_collector = reference_collector
        self.config = config
        self.module_discovery = module_discovery
        self.source_root = source_root or Path.cwd() / "src"
        self.export_service = export_service
        self.force_export = force_export # For targeted workflows
        self.export_formats = export_formats or ["html"]
        
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.data: Dict[str, Any] = {}
        self.timings: Dict[str, float] = {}
        self.summary_builder = SummaryDataBuilder()
        
        # Targets
        self.unit_target = unit_target
        self.e2e_target = e2e_target
        self.quality_target = quality_target
        
        # Dynamic State
        self.cover_metadata: Dict[str, Any] = {}
        
    def add_timing(self, stage: str, duration: float) -> None:
        self.timings[stage] = duration
        
    def get_timing(self, stage: str) -> float:
        return self.timings.get(stage, 0.0)
