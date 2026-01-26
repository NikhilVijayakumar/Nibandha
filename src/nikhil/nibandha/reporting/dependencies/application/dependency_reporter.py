
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from ...shared.infrastructure.visualizers import matplotlib_impl as visualizer
from ...shared.infrastructure import utils
from ...dependencies.infrastructure.analysis.module_scanner import ModuleScanner
from ...shared.rendering.template_engine import TemplateEngine
from ...shared.domain.grading import Grader
from ...shared.domain.reference_models import FigureReference, TableReference, NomenclatureItem

if TYPE_CHECKING:
    from ...shared.domain.protocols.reference_collector_protocol import ReferenceCollectorProtocol

logger = logging.getLogger("nibandha.reporting.dependencies")

class DependencyReporter:
    def __init__(
        self, 
        output_dir: Path, 
        templates_dir: Path,
        template_engine: TemplateEngine = None,
        reference_collector: "ReferenceCollectorProtocol" = None
    ):
        self.output_dir = output_dir
        self.templates_dir = templates_dir
        self.report_dir = output_dir / "details"
        self.assets_dir = output_dir / "assets" / "images" / "dependencies"
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        
        self.template_engine = template_engine or TemplateEngine(templates_dir)
        self.reference_collector = reference_collector

    def generate(self, source_root: Path, package_roots: List[str] = None, project_name: str = "Project") -> Dict:
        """Generates module dependency report."""
        logger.info(f"Scanning dependencies in {source_root}...")
        
        scanner = ModuleScanner(source_root, package_roots)
        dependencies = scanner.scan()
        
        circular_deps = scanner.find_circular_dependencies()
        most_imported = scanner.get_most_imported()
        most_dependent = scanner.get_most_dependent()
        isolated = scanner.get_isolated_modules()
        
        # Visuals
        visualizer.plot_dependency_graph(dependencies, self.assets_dir / "module_dependencies.png", circular_deps)
        visualizer.plot_dependency_matrix(dependencies, self.assets_dir / "dependency_matrix.png")
        
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

    def _generate_report(self, dependencies, circular, most_imported, most_dependent, isolated, project_name="Project"):
        # Format lists
        imp_rows = "\n".join([f"| {m} | {c} |" for m, c in most_imported])
        dep_rows = "\n".join([f"| {m} | {c} |" for m, c in most_dependent])
        iso_list = ", ".join(isolated) if isolated else "None"
        
        circ_text = "None detected."
        if circular:
            circ_text = "\n".join([f"- {a} <-> {b}" for a, b in circular])

        # Calculate Per-Module Grades
        module_grades = []
        circular_modules = set()
        for a, b in circular:
            circular_modules.add(a)
            circular_modules.add(b)
            
        fan_in = {}
        for mod, deps in dependencies.items():
            if mod not in fan_in: fan_in[mod] = 0
            for dep in deps:
                fan_in[dep] = fan_in.get(dep, 0) + 1
        
        for mod, deps in dependencies.items():
            f_out = len(deps)
            f_in = fan_in.get(mod, 0)
            is_circular = mod in circular_modules
            
            if is_circular:
                grade = "F"
                reason = "Circular Dependency"
            elif f_out > 12:
                grade = "D"
                reason = "High Coupling (12+)"
            elif f_out > 7:
                grade = "C"
                reason = "Moderate Coupling (8-12)"
            elif f_out > 3:
                grade = "B"
                reason = "Low Coupling (4-7)"
            else:
                grade = "A"
                reason = "Clean"
                
            color = Grader.get_grade_color(grade)
            grade_html = f'<span style="color:{color}; font-weight:bold">{grade}</span>'
            
            module_grades.append({
                "name": mod,
                "fan_out": f_out,
                "fan_in": f_in,
                "grade": grade,
                "grade_html": grade_html,
                "reason": reason
            })
            
        module_grades.sort(key=lambda x: (x["grade"], x["name"]))
        
        grade_rows = ""
        for m in module_grades:
            grade_rows += f"| {m['name']} | {m['fan_out']} | {m['fan_in']} | {m['reason']} | {m['grade_html']} |\n"
            
        if not grade_rows:
            grade_rows = "| No modules found | - | - | - | - |"

        grade = Grader.calculate_dependency_grade(len(circular))
        
        avg_deps = round(sum(len(deps) for deps in dependencies.values()) / len(dependencies), 2) if dependencies else 0
        overall_status = "Healthy" if not circular and len(isolated) == 0 else "Needs Attention"
        circ_status = "🔴 Critical" if circular else "🟢 None"
        iso_status = "🟡 Warning" if isolated else "🟢 None"

        import datetime
        mapping = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "overall_status": overall_status,
            "display_grade": grade,
            "grade_color": Grader.get_grade_color(grade),
            
            "total_modules": len(dependencies),
            "total_deps": sum(len(deps) for deps in dependencies.values()),
            "circular_deps": len(circular),
            "circular_status": circ_status,
            "isolated": len(isolated),
            "isolated_status": iso_status,
            "avg_deps": avg_deps,
            
            "top_imported": imp_rows if imp_rows else "| None | - | - |",
            "top_importers": dep_rows if dep_rows else "| None | - | - |",
            "module_grades_table": grade_rows,
            
            "circular_deps_list": circ_text,
            "isolated_modules_list": iso_list,
            "detailed_dependency_list": "\n".join([f"- **{m}**: {', '.join(d)}" for m, d in dependencies.items()]),
            
            "high_priority_items": "None generated.",
            "recommendations": "None generated.",
            "project_name": project_name
        }
        
        # Register References (Order 8)
        if self.reference_collector:
            self.reference_collector.add_figure(FigureReference(
                id="fig-module-deps",
                title="Module dependency graph",
                path="../assets/images/dependencies/module_dependencies.png",
                type="network_graph",
                description="Visual representation of module inter-dependencies",
                source_report="dependencies",
                report_order=8
            ))
            self.reference_collector.add_figure(FigureReference(
                id="fig-dep-matrix",
                title="Dependency matrix",
                path="../assets/images/dependencies/dependency_matrix.png",
                type="matrix",
                description="Adjacency matrix of module dependencies",
                source_report="dependencies",
                report_order=8
            ))
            self.reference_collector.add_table(TableReference(
                id="table-module-grades",
                title="Module coupling grades",
                description="Assessment of module coupling (fan-in/fan-out) and cyclomatic dependencies",
                source_report="dependencies",
                report_order=8
            ))
        
        self.template_engine.render("module_dependency_template.md", mapping, self.report_dir / "08_module_dependency_report.md")
