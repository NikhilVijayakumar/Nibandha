
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from ...shared.infrastructure.visualizers import matplotlib_impl as visualizer
from ...shared.infrastructure import utils
from ...dependencies.infrastructure.analysis.package_scanner import PackageScanner
from ...shared.rendering.template_engine import TemplateEngine
from ...shared.domain.grading import Grader
from ...shared.domain.reference_models import FigureReference, TableReference, NomenclatureItem
import datetime

if TYPE_CHECKING:
    from ...shared.domain.protocols.reference_collector_protocol import ReferenceCollectorProtocol

logger = logging.getLogger("nibandha.reporting.packages")

class PackageReporter:
    def __init__(
        self, 
        output_dir: Path, 
        templates_dir: Path,
        template_engine: Optional[TemplateEngine] = None,
        reference_collector: Optional["ReferenceCollectorProtocol"] = None
    ):
        self.output_dir = output_dir
        self.templates_dir = templates_dir
        self.report_dir = output_dir / "details"
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        self.template_engine = template_engine or TemplateEngine(templates_dir)
        self.reference_collector = reference_collector

    def generate(self, project_root: Path, project_name: str = "Project") -> Dict[str, Any]:
        """Generates package dependency report."""
        logger.info(f"Analyzing packages in {project_root}...")
        
        scanner = PackageScanner(project_root)
        analysis = scanner.analyze()
        
        self._generate_report(analysis, project_name)
        
        score = 100
        score -= (analysis.get("major_updates", 0) * 20)
        score -= (analysis.get("minor_updates", 0) * 5)
        score = max(0, score)
        
        status = "PASS" if score > 80 else "FAIL"
        grade = Grader.calculate_package_grade(score)
        
        return {
            "status": status,
            "grade": grade,
            "total_packages": analysis.get("installed_count", 0),
            "outdated_count": analysis.get("outdated_count", 0),
            "health_score": score
        }

    def _generate_report(self, analysis: Dict[str, Any], project_name: str = "Project") -> None:
        outdated_rows = ""
        for p in analysis["outdated_packages"]:
            icon = "🔴" if p["update_type"] == "MAJOR" else ("🟡" if p["update_type"] == "MINOR" else "🟢")
            outdated_rows += f"| {icon} {p['name']} | `{p['version']}` | `{p['latest_version']}` | {p['update_type']} |\n"
            
        unused_rows = ""
        for p in analysis["unused_packages"]:
            unused_rows += f"- {p}\n"
            
        if not outdated_rows: outdated_rows = "| - | - | - | - |"
        if not unused_rows: unused_rows = "None detected."
        
        all_outdated = analysis.get("outdated_packages", [])
        major_list = [p for p in all_outdated if p["update_type"] == "MAJOR"]
        minor_list = [p for p in all_outdated if p["update_type"] == "MINOR"]
        patch_list = [p for p in all_outdated if p["update_type"] == "PATCH"]

        score = 100
        score -= (analysis["major_updates"] * 20)
        score -= (analysis["minor_updates"] * 5)
        score = max(0, score)
        
        grade = Grader.calculate_package_grade(score)
        overall = "Healthy" if score > 80 else ("Needs Attention" if score > 50 else "Critical")
        
        full_list = "\n".join([f"- {name} ({ver})" for name, ver in analysis.get('installed_packages', {}).items()])

        mapping = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "display_grade": grade,
            "grade_color": Grader.get_grade_color(grade),
            "overall_status": overall,
            
            "installed_count": analysis["installed_count"],
            "declared_count": analysis["declared_count"],
            "up_to_date": analysis["up_to_date_count"],
            
            "outdated": analysis["outdated_count"],
            "outdated_status": "🟢" if analysis["outdated_count"] == 0 else "🟡",
            
            "major_updates": analysis["major_updates"],
            "major_status": "🟢" if analysis["major_updates"] == 0 else "🔴",
            
            "minor_updates": analysis["minor_updates"],
            "patch_updates": analysis["patch_updates"],
            "unused": analysis["unused_count"],
            
            "health_score": score,
            "points_current": 0,
            "points_minor": analysis["minor_updates"] * 5,
            "points_major": analysis["major_updates"] * 20,
            "points_security": 0,
            
            "package_table": outdated_rows if outdated_rows != "| - | - | - | - |" else "| All packages up to date | - | - | - | - | - |",
            
            "major_updates_detail": "\n".join([f"- {p['name']}: {p['version']} -> {p['latest_version']}" for p in major_list]) or "None",
            "security_advisories": "No advisories detected.",
            
            "minor_updates_detail": "\n".join([f"- {p['name']}: {p['version']} -> {p['latest_version']}" for p in minor_list]) or "None",
            "patch_updates_detail": "\n".join([f"- {p['name']}: {p['version']} -> {p['latest_version']}" for p in patch_list]) or "None",
            
            "unused_deps_detail": unused_rows,
            "dev_vs_prod_breakdown": "Analysis not available.",
            
            "immediate_actions": "Review major updates." if major_list else "None.",
            "short_term_actions": "Review unused dependencies.",
            "long_term_actions": "Monitor for new updates.",
            
            "full_package_list": full_list,
            "project_name": project_name
        }
        
        # Register References (Order 12)
        if self.reference_collector:
            self.reference_collector.add_table(TableReference(
                id="table-outdated-packages",
                title="Outdated packages",
                description="List of packages with available updates",
                source_report="packages",
                report_order=12
            ))
            # No figures for now as per code
        
        self.template_engine.render("package_dependency_template.md", mapping, self.report_dir / "12_package_dependency_report.md")
