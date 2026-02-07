from pathlib import Path
from typing import Dict, Any, List
import logging

from nibandha.reporting.shared.infrastructure.visualizers.plotters.unit_plotter import UnitPlotter
from nibandha.reporting.shared.infrastructure.visualizers.plotters.e2e_plotter import E2EPlotter
from nibandha.reporting.shared.infrastructure.visualizers.plotters.quality_plotter import QualityPlotter
from nibandha.reporting.shared.infrastructure.visualizers.plotters.hygiene_plotter import HygienePlotter
from nibandha.reporting.shared.infrastructure.visualizers.plotters.security_plotter import SecurityPlotter
from nibandha.reporting.shared.infrastructure.visualizers.plotters.duplication_plotter import DuplicationPlotter
from nibandha.reporting.shared.infrastructure.visualizers.plotters.encoding_plotter import EncodingPlotter
from nibandha.reporting.shared.infrastructure.visualizers.plotters.dependency_plotter import DependencyPlotter
from nibandha.reporting.shared.infrastructure.visualizers.plotters.documentation_plotter import DocumentationPlotter
from nibandha.reporting.shared.infrastructure.visualizers.plotters.performance_plotter import PerformancePlotter
from nibandha.reporting.shared.infrastructure.visualizers.plotters.conclusion_plotter import ConclusionPlotter

logger = logging.getLogger("nibandha.reporting")

class DefaultVisualizationProvider:
    """
    Default implementation of visualization generation.
    Uses modular plotters via composition.
    """
    
    def __init__(self):
        self.unit_plotter = UnitPlotter()
        self.e2e_plotter = E2EPlotter()
        self.quality_plotter = QualityPlotter()
        self.hygiene_plotter = HygienePlotter()
        self.security_plotter = SecurityPlotter()
        self.duplication_plotter = DuplicationPlotter()
        self.encoding_plotter = EncodingPlotter()
        self.dependency_plotter = DependencyPlotter()
        self.doc_plotter = DocumentationPlotter()
        self.perf_plotter = PerformancePlotter()
        self.conclusion_plotter = ConclusionPlotter()

    def generate_unit_test_charts(self, data: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
        return self.unit_plotter.plot(data, output_dir)
    
    def generate_e2e_test_charts(self, data: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
        return self.e2e_plotter.plot(data, output_dir)
    
    def generate_type_safety_charts(self, data: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
        return self.quality_plotter.plot_type_safety(data, output_dir)
    
    def generate_complexity_charts(self, data: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
        return self.quality_plotter.plot_complexity(data, output_dir)
    
    def generate_architecture_charts(self, data: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
        return self.quality_plotter.plot_architecture(data, output_dir)

    def generate_documentation_charts(self, data: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
        return self.doc_plotter.plot(data, output_dir)

    def generate_performance_charts(self, timings: List[Dict[str, Any]], output_dir: Path) -> Dict[str, str]:
        return self.perf_plotter.plot(timings, output_dir)
    
    def generate_hygiene_charts(self, data: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
        return self.hygiene_plotter.plot(data, output_dir)

    def generate_security_charts(self, data: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
        return self.security_plotter.plot(data, output_dir)

    def generate_duplication_charts(self, data: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
        return self.duplication_plotter.plot(data, output_dir)

    def generate_encoding_charts(self, data: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
        return self.encoding_plotter.plot(data, output_dir)
    
    def generate_conclusion_charts(self, scores: Dict[str, Dict[str, str]], output_dir: Path) -> Dict[str, str]:
        return self.conclusion_plotter.plot(scores, output_dir)
    
    def generate_dependency_charts(self, dependencies: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
         return self.dependency_plotter.plot(dependencies, output_dir)
