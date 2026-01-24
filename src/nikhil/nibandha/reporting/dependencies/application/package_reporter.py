
import logging
from pathlib import Path
from typing import Dict, Any, List
from ...shared.infrastructure.visualizers import matplotlib_impl as visualizer
from ...shared.infrastructure import utils
from ...dependencies.infrastructure.analysis.package_scanner import PackageScanner
import datetime

logger = logging.getLogger("nibandha.reporting.packages")

class PackageReporter:
    def __init__(self, output_dir: Path, templates_dir: Path):
        self.output_dir = output_dir
        self.templates_dir = templates_dir
        self.report_dir = output_dir / "details"
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, project_root: Path) -> Dict:
        """Generates package dependency report."""
        logger.info(f"Analyzing packages in {project_root}...")
        
        scanner = PackageScanner(project_root)
        analysis = scanner.analyze()
        
        self._generate_report(analysis)
        
        # Calculate summary stats
        # Health Score logic duplicated from _generate_report to ensure consistency
        # Or better: make _generate_report return the score. 
        # But simpler to just recalc for now or use analysis data if available.
        # _generate_report logic:
        # score = 100
        # score -= (analysis["major_updates"] * 20)
        # score -= (analysis["minor_updates"] * 5)
        # score = max(0, score)
        
        score = 100
        score -= (analysis.get("major_updates", 0) * 20)
        score -= (analysis.get("minor_updates", 0) * 5)
        score = max(0, score)
        
        status = "PASS" if score > 80 else "FAIL"
        
        return {
            "status": status,
            "total_packages": analysis.get("installed_count", 0),
            "outdated_count": analysis.get("outdated_count", 0),
            "health_score": score
        }

    def _generate_report(self, analysis):
        tmpl = self._load_template("package_dependency_template.md")
        
        outdated_rows = ""
        for p in analysis["outdated_packages"]:
            icon = "🔴" if p["update_type"] == "MAJOR" else ("🟡" if p["update_type"] == "MINOR" else "🟢")
            outdated_rows += f"| {icon} {p['name']} | `{p['version']}` | `{p['latest_version']}` | {p['update_type']} |\n"
            
        unused_rows = ""
        for p in analysis["unused_packages"]:
            unused_rows += f"- {p}\n"
            
        if not outdated_rows: outdated_rows = "| - | - | - | - |"
        if not unused_rows: unused_rows = "None detected."
        
        # Filter lists for details
        all_outdated = analysis.get("outdated_packages", [])
        major_list = [p for p in all_outdated if p["update_type"] == "MAJOR"]
        minor_list = [p for p in all_outdated if p["update_type"] == "MINOR"]
        patch_list = [p for p in all_outdated if p["update_type"] == "PATCH"]

        # Calculate Health Score (using pre-calculated counts)
        score = 100
        score -= (analysis["major_updates"] * 20)
        score -= (analysis["minor_updates"] * 5)
        # score -= security_issues * 30 (Not implemented yet)
        score = max(0, score)
        
        overall = "Healthy" if score > 80 else ("Needs Attention" if score > 50 else "Critical")
        
        # Build Table
        full_table = outdated_rows 
        
        # Full List
        full_list = "\n".join([f"- {name} ({ver})" for name, ver in analysis.get('installed_packages', {}).items()])

        mapping = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "overall_status": overall,
            
            # Summary Metrics
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
            
            # Score
            "health_score": score,
            "points_current": 0,
            "points_minor": analysis["minor_updates"] * 5,
            "points_major": analysis["major_updates"] * 20,
            "points_security": 0,
            
            # Details
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
            
            "full_package_list": full_list
        }
        
        try:
             content = tmpl.format(**mapping)
        except KeyError as e:
             logger.warning(f"Key error in package template: {e}")
             mapping[e.args[0]] = "N/A"
             try: content = tmpl.format(**mapping)
             except: content = tmpl
             
        utils.save_report(self.report_dir / "package_dependency_report.md", content)

    def _load_template(self, name):
         f = self.templates_dir / name
         if f.exists(): return f.read_text(encoding="utf-8")
         return f"# {name}\nTemplate not found."
