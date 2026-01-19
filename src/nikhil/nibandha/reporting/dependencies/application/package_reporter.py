
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

    def generate(self, project_root: Path):
        """Generates package dependency report."""
        logger.info(f"Analyzing packages in {project_root}...")
        
        scanner = PackageScanner(project_root)
        analysis = scanner.analyze()
        
        self._generate_report(analysis)

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
        
        mapping = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "installed_count": analysis["installed_count"],
            "declared_count": analysis["declared_count"],
            "up_to_date_count": analysis["up_to_date_count"],
            "outdated_count": analysis["outdated_count"],
            "unused_count": analysis["unused_count"],
            "major_updates": analysis["major_updates"],
            "minor_updates": analysis["minor_updates"],
            "patch_updates": analysis["patch_updates"],
            "outdated_table": outdated_rows,
            "unused_list": unused_rows
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
