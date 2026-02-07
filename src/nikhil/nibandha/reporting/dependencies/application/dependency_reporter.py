
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, TYPE_CHECKING, Tuple, TYPE_CHECKING
from nibandha.reporting.shared.infrastructure import utils
from nibandha.reporting.shared.infrastructure.visualizers.default_visualizer import DefaultVisualizationProvider
from nibandha.reporting.shared.domain.protocols.visualization_protocol import VisualizationProvider
from nibandha.reporting.shared.domain.protocols.template_provider_protocol import TemplateProviderProtocol
from nibandha.reporting.dependencies.infrastructure.analysis.module_scanner import ModuleScanner
from nibandha.reporting.shared.rendering.template_engine import TemplateEngine
from nibandha.reporting.shared.domain.grading import Grader
from nibandha.reporting.shared.domain.reference_models import FigureReference, TableReference
from nibandha.reporting.shared.constants import (
    REPORT_ORDER_DEPENDENCY, ASSETS_IMAGES_DIR_REL,
    IMG_PATH_MODULE_DEPENDENCIES, IMG_PATH_DEPENDENCY_MATRIX
)
from nibandha.reporting.shared.domain.protocols.reference_collector_protocol import ReferenceCollectorProtocol

logger = logging.getLogger("nibandha.reporting.dependencies")

class DependencyReporter:
    def __init__(
        self, 
        output_dir: Path, 
        templates_dir: Path,
        template_engine: Optional[TemplateProviderProtocol] = None,
        viz_provider: Optional[VisualizationProvider] = None,
        reference_collector: Optional["ReferenceCollectorProtocol"] = None
    ):
        self.output_dir = output_dir
        self.templates_dir = templates_dir
        self.report_dir = output_dir / "details"
        self.assets_dir = output_dir / "assets" / "images" / "dependencies"
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        
        self.template_engine = template_engine or TemplateEngine(templates_dir)
        self.viz_provider = viz_provider or DefaultVisualizationProvider()
        self.reference_collector = reference_collector

    def generate(self, source_root: Path, package_roots: Optional[List[str]] = None, project_name: str = "Project") -> Dict[str, Any]:
        """Generates module dependency report."""
        logger.info(f"Scanning dependencies in {source_root}...")
        
        scanner = ModuleScanner(source_root, package_roots)
        dependencies = scanner.scan()
        
        circular_deps = scanner.find_circular_dependencies()
        most_imported = scanner.get_most_imported()
        most_dependent = scanner.get_most_dependent()
        isolated = scanner.get_isolated_modules()
        
        # Visuals
        self.viz_provider.generate_dependency_charts(dependencies, self.assets_dir)
        
        # Report
        self._generate_report(dependencies, circular_deps, most_imported, most_dependent, isolated, project_name)
        
        # Return summary data
        total_modules = len(dependencies)
        total_deps = sum(len(deps) for deps in dependencies.values())
        
        return {
            "status": "PASS" if not circular_deps else "FAIL",
            "total_modules": total_modules,
            "total_dependencies": total_deps,
            "circular_count": len(circular_deps)
        }

    def _generate_report(self, dependencies: Dict[str, Any], circular: List[Any], most_imported: List[Any], most_dependent: List[Any], isolated: List[str], project_name: str = "Project") -> None:
        # Calculate Metrics & Grades
        module_grades = self._calculate_module_grades(dependencies, circular)
        
        # Prepare Report Data
        mapping = self._prepare_report_data(
            dependencies, circular, isolated, 
            most_imported, most_dependent, 
            module_grades, project_name
        )
        
        # Register References
        if self.reference_collector:
            self._register_references()
        
        self.template_engine.render("module_dependency_template.md", mapping, self.report_dir / "11_module_dependency_report.md")

    def _calculate_module_grades(self, dependencies: Dict[str, Any], circular_pairs: List[Any]) -> List[Dict[str, Any]]:
        module_grades = []
        circular_modules = {a for pair in circular_pairs for a in pair}
        
        fan_in = self._calculate_fan_in(dependencies)
        
        for mod, deps in dependencies.items():
            f_out = len(deps)
            f_in = fan_in.get(mod, 0)
            
            grade, reason = self._determine_grade(mod, f_out, circular_modules)
            color = Grader.get_grade_color(grade) # type: ignore
            grade_html = f'<span style="color:{color}; font-weight:bold">{grade}</span>'
            
            module_grades.append({
                "name": mod, "fan_out": f_out, "fan_in": f_in,
                "grade": grade, "grade_html": grade_html, "reason": reason
            })
            
        module_grades.sort(key=lambda x: (x["grade"], x["name"]))
        return module_grades

    def _calculate_fan_in(self, dependencies: Dict[str, Any]) -> Dict[str, int]:
        fan_in = {}
        for mod, deps in dependencies.items():
            if mod not in fan_in: fan_in[mod] = 0
            for dep in deps:
                fan_in[dep] = fan_in.get(dep, 0) + 1
        return fan_in

    def _determine_grade(self, mod: str, f_out: int, circular_modules: Any) -> Tuple[str, str]:
        from nibandha.reporting.shared.constants import COUPLING_HIGH_THRESHOLD, COUPLING_MODERATE_THRESHOLD, COUPLING_LOW_THRESHOLD
        
        if mod in circular_modules:
            return "F", "Circular Dependency"
        elif f_out > COUPLING_HIGH_THRESHOLD:
            return "D", f"High Coupling ({COUPLING_HIGH_THRESHOLD}+)"
        elif f_out > COUPLING_MODERATE_THRESHOLD:
            return "C", f"Moderate Coupling ({COUPLING_MODERATE_THRESHOLD+1}-{COUPLING_HIGH_THRESHOLD})"
        elif f_out > COUPLING_LOW_THRESHOLD:
            return "B", f"Low Coupling ({COUPLING_LOW_THRESHOLD+1}-{COUPLING_MODERATE_THRESHOLD})"
        return "A", "Clean"

    def _prepare_report_data(self, dependencies: Dict[str, Any], circular: List[Any], isolated: List[str], most_imported: List[Any], most_dependent: List[Any], module_grades: List[Dict[str, Any]], project_name: str) -> Dict[str, Any]:
        import datetime
        
        grade = Grader.calculate_dependency_grade(len(circular))
        avg_deps = round(sum(len(deps) for deps in dependencies.values()) / len(dependencies), 2) if dependencies else 0
        
        # Tables
        imp_rows = "\n".join([f"| {m} | {c} |" for m, c in most_imported]) if most_imported else "| None | - | - |"
        dep_rows = "\n".join([f"| {m} | {c} |" for m, c in most_dependent]) if most_dependent else "| None | - | - |"
        
        grade_rows = ""
        for m in module_grades:
            grade_rows += f"| {m['name']} | {m['fan_out']} | {m['fan_in']} | {m['reason']} | {m['grade_html']} |\n"
        if not grade_rows: grade_rows = "| No modules found | - | - | - | - |"

        circ_text = "\n".join([f"- {a} <-> {b}" for a, b in circular]) if circular else "None detected."
        iso_list = ", ".join(isolated) if isolated else "None"

        return {
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "overall_status": "Healthy" if not circular and not isolated else "Needs Attention",
            "display_grade": grade,
            "grade_color": Grader.get_grade_color(grade),
            "total_modules": len(dependencies),
            "total_deps": sum(len(deps) for deps in dependencies.values()),
            "circular_deps": len(circular),
            "circular_status": "🔴 Critical" if circular else "🟢 None",
            "isolated": len(isolated),
            "isolated_status": "🟡 Warning" if isolated else "🟢 None",
            "avg_deps": avg_deps,
            "top_imported": imp_rows,
            "top_importers": dep_rows,
            "module_grades_table": grade_rows,
            "circular_deps_list": circ_text,
            "isolated_modules_list": iso_list,
            "detailed_dependency_list": "\n".join([f"- **{m}**: {', '.join(d)}" for m, d in dependencies.items()]),
            "high_priority_items": "None generated.",
            "recommendations": "None generated.",
            "project_name": project_name
        }

    def _register_references(self) -> None:
        if not self.reference_collector: return
        self.reference_collector.add_figure(FigureReference(
            id="fig-module-deps",
            title="Module Dependency Map",
            path=IMG_PATH_MODULE_DEPENDENCIES,
            type="network_graph",
            description="Visual representation of module inter-dependencies",
            source_report="dependencies",
            report_order=REPORT_ORDER_DEPENDENCY
        ))
        self.reference_collector.add_figure(FigureReference(
            id="fig-dep-matrix",
            title="Dependency Adjacency Matrix",
            path=IMG_PATH_DEPENDENCY_MATRIX,
            type="matrix",
            description="Adjacency matrix of module dependencies",
            source_report="dependencies",
            report_order=REPORT_ORDER_DEPENDENCY
        ))
        self.reference_collector.add_table(TableReference(
            id="table-module-grades",
            title="Module coupling grades",
            description="Assessment of module coupling (fan-in/fan-out) and cyclomatic dependencies",
            source_report="dependencies",
            report_order=REPORT_ORDER_DEPENDENCY
        ))
