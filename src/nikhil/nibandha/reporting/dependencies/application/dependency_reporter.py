
import logging
from pathlib import Path
from typing import Dict, Any, List
from ...shared.infrastructure.visualizers import matplotlib_impl as visualizer
from ...shared.infrastructure import utils
from ...dependencies.infrastructure.analysis.module_scanner import ModuleScanner
import datetime
from ...shared.domain.grading import Grader

logger = logging.getLogger("nibandha.reporting.dependencies")

class DependencyReporter:
    def __init__(self, output_dir: Path, templates_dir: Path):
        self.output_dir = output_dir
        self.templates_dir = templates_dir
        self.report_dir = output_dir / "details"
        self.assets_dir = output_dir / "assets" / "images" / "dependencies"
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, source_root: Path, package_roots: List[str] = None):
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
        self._generate_report(dependencies, circular_deps, most_imported, most_dependent, isolated)

    def _generate_report(self, dependencies, circular, most_imported, most_dependent, isolated):
        tmpl = self._load_template("module_dependency_template.md")
        
        # Format lists
        imp_rows = "\n".join([f"| {m} | {c} |" for m, c in most_imported])
        dep_rows = "\n".join([f"| {m} | {c} |" for m, c in most_dependent])
        iso_list = ", ".join(isolated) if isolated else "None"
        
        circ_text = "None detected."
        if circular:
            circ_text = "\n".join([f"- {a} <-> {b}" for a, b in circular])

        # Grade
        grade = Grader.calculate_dependency_grade(len(circular))
        
        # Calculate Statuses
        avg_deps = round(sum(len(deps) for deps in dependencies.values()) / len(dependencies), 2) if dependencies else 0
        overall_status = "Healthy" if not circular and len(isolated) == 0 else "Needs Attention"
        circ_status = "🔴 Critical" if circular else "🟢 None"
        iso_status = "🟡 Warning" if isolated else "🟢 None"

        mapping = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "overall_status": overall_status,
            "display_grade": grade,
            "grade_color": Grader.get_grade_color(grade),
            
            # Executive Summary
            "total_modules": len(dependencies),
            "total_deps": sum(len(deps) for deps in dependencies.values()),
            "circular_deps": len(circular),
            "circular_status": circ_status,
            "isolated": len(isolated),
            "isolated_status": iso_status,
            "avg_deps": avg_deps,
            
            # Tables
            "top_imported": imp_rows if imp_rows else "| None | - | - |",
            "top_importers": dep_rows if dep_rows else "| None | - | - |",
            
            # Lists
            "circular_deps_list": circ_text,
            "isolated_modules_list": iso_list,
            "detailed_dependency_list": "\n".join([f"- **{m}**: {', '.join(d)}" for m, d in dependencies.items()]),
            
            # Placeholders for unimplemented sections
            "high_priority_items": "None generated.",
            "recommendations": "None generated."
        }
        
        try:
            content = tmpl.format(**mapping)
        except KeyError as e:
            logger.warning(f"Missing key in dependency template: {e}")
            mapping[e.args[0]] = "N/A"
            try:
                content = tmpl.format(**mapping)
            except:
                content = tmpl
                
        utils.save_report(self.report_dir / "module_dependency_report.md", content)

    def _load_template(self, name):
         # Check if template exists in templates_dir, else try package default (if passed correctly)
         # In generic core.py we pass templates_dir.
         f = self.templates_dir / name
         if f.exists():
             return f.read_text(encoding="utf-8")
         # Fallback logic if needed, but ReportGenerator handles setting up templates_dir
         return f"# {name}\nTemplate not found."
