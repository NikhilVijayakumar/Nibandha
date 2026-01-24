import shutil
import sys
import subprocess
import re
import datetime
from pathlib import Path
from typing import Dict, Any, List
import logging
from ...shared.domain.grading import Grader
from ...shared.infrastructure.visualizers import matplotlib_impl as visualizer
from ...shared.infrastructure import utils
from ...shared.rendering.template_engine import TemplateEngine
from ...shared.domain.protocols.visualization_protocol import VisualizationProvider
from ...shared.infrastructure.visualizers.default_visualizer import DefaultVisualizationProvider

logger = logging.getLogger("nibandha.reporting.quality")

class QualityReporter:
    def __init__(
        self, 
        output_dir: Path, 
        templates_dir: Path,
        template_engine: TemplateEngine = None,
        viz_provider: VisualizationProvider = None
    ):
        self.output_dir = output_dir
        self.templates_dir = templates_dir
        
        # Write reports to "data" to match Unit/E2E behavior and test expectations
        # Ideally reports go to a 'reports' folder and data to 'data', but tests expect 'data/*.md'
        self.details_dir = output_dir / "details"
        self.data_dir = output_dir / "assets" / "data" / "quality"
        self.images_dir = output_dir / "assets" / "images" / "quality"
        
        self.details_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)

        self.template_engine = template_engine or TemplateEngine(templates_dir)
        self.viz_provider = viz_provider or DefaultVisualizationProvider()

    def run_checks(self, target_package: str = "src/nikhil/nibandha") -> Dict[str, Any]:
        """Runs quality checks and returns results."""
        results = {
            "architecture": self._run_architecture_check(),
            "type_safety": self._run_type_check(target_package),
            "complexity": self._run_complexity_check(target_package),
        }
        
        # Calculate overall quality grade? 
        # Actually generate methods will enrich data with grades.
        return results

    def generate(self, results: Dict[str, Any]):
        """Generates all quality reports using Template Engine."""
        logger.info("Generating Quality Reports (Architecture, Type Safety, Complexity)")
        # Architecture
        self._generate_architecture_report(results["architecture"])
        # Type Safety
        self._generate_type_safety_report(results["type_safety"])
        # Complexity
        self._generate_complexity_report(results["complexity"])
        # Overview
        self._generate_overview(results)

    def _generate_architecture_report(self, data):
        # Grade Calculation
        status_pass = (data["status"] == "PASS")
        violation_count = 0 if status_pass else 1 # Simple boolean logic for now
        grade = Grader.calculate_quality_grade(violation_count, is_fatal=not status_pass)
        data["grade"] = grade
        
        # 1. Visualize
        chart_path = self.images_dir / "architecture_status.png"
        self.viz_provider.generate_architecture_charts(data, self.images_dir)
        
        # 2. Enrich Data for Template
        status = data["status"]
        output_text = data["output"]
        
        if "cannot find the file" in output_text.lower() or "no such file" in output_text.lower():
             detailed_violations = "⚠️ **Configuration Missing**\n.importlinter file not found."
             status = "⚠️ NOT CONFIGURED"
        elif status == "PASS":
             detailed_violations = "✅ **No violations detected**"
             status = "🟢 PASS"
        else:
             detailed_violations = f"```\n{output_text}\n```"
             status = "🔴 FAIL"
             
        mapping = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "display_grade": grade,
            "grade_color": Grader.get_grade_color(grade),
            "overall_status": status,
            "detailed_violations": detailed_violations,
            "module_breakdown": f"## Module Breakdown\nPleasure refer to detailed violations.",
            "status": status, # raw status just in case
            "arch_status": status,
            "arch_violations": "-",
            # Add placeholders for template keys if they exist
            "struct_status": "N/A", "struct_violations": "N/A"
        }
        
        if "PASS" in status:
             mapping["module_breakdown"] = (
                "## 📦 Module Breakdown\n\n"
                "| Module | Status | Violations |\n"
                "| :--- | :---: | :---: |\n"
                f"| **Project** | PASS | - |"
            )

        # 3. Render
        self.template_engine.render("architecture_report_template.md", mapping, self.details_dir / "architecture_report.md")

    def _generate_type_safety_report(self, data):
        # Grade
        total_errors = data["violation_count"]
        grade = Grader.calculate_quality_grade(total_errors)
        data["grade"] = grade
        
        # 1. Visualize
        enriched_viz_data = {"errors_by_module": {}, "errors_by_category": {}}
        errors_by_module, errors_by_category = self._parse_mypy_output(data["output"])
        enriched_viz_data["errors_by_module"] = errors_by_module
        enriched_viz_data["errors_by_category"] = errors_by_category
        
        self.viz_provider.generate_type_safety_charts(enriched_viz_data, self.images_dir)

        # 2. Enrich
        total_errors = data["violation_count"]
        overall_status = "🟢 PASS" if total_errors == 0 else "🔴 FAIL"
        
        category_table = "| Error Type | Count | Percentage |\n| :--- | :---: | :---: |\n"
        sorted_categories = sorted(errors_by_category.items(), key=lambda x: x[1], reverse=True)
        for cat, count in sorted_categories[:10]:
             pct = (count / total_errors * 100) if total_errors > 0 else 0
             category_table += f"| `{cat}` | {count} | {pct:.1f}% |\n"
             
        error_lines = [line for line in data["output"].splitlines() if "error:" in line]
        detailed_errors = "\n".join(error_lines[:30])
        if len(error_lines) > 30:
             detailed_errors += f"\n\n... and {len(error_lines) - 30} more errors"
        detailed_errors = f"```\n{detailed_errors}\n```"

        mapping = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "display_grade": grade,
            "grade_color": Grader.get_grade_color(grade),
            "overall_status": overall_status,
            "total_errors": total_errors,
            "category_table": category_table,
            "detailed_errors": detailed_errors,
            "type_status": overall_status,
            "type_violations": total_errors
        }
        
        # Generate dynamic module table based on actual errors
        module_table = "| Module | Status | Errors |\n| :--- | :---: | :---: |\n"
        if errors_by_module:
            for module, error_count in sorted(errors_by_module.items(), key=lambda x: x[1], reverse=True):
                status = "🟢" if error_count == 0 else "🔴"
                module_table += f"| **{module}** | {status} | {error_count} |\n"
        else:
            module_table += "| **All Modules** | 🟢 | 0 |\n"
        
        mapping["module_table"] = module_table

        # 3. Render
        self.template_engine.render("type_safety_report_template.md", mapping, self.details_dir / "type_safety_report.md")

    def _generate_complexity_report(self, data):
        # Grade
        # Need partial parse first to get total? no, Data has violation_count now?
        # Check run_complexity_check return. Yes, it has violation_count.
        total = data["violation_count"]
        grade = Grader.calculate_quality_grade(total)
        data["grade"] = grade

        # 1. Visualize
        violations = self._parse_ruff_output(data["output"])
        self.viz_provider.generate_complexity_charts({"violations_by_module": violations}, self.images_dir)
        
        # 2. Enrich
        total = sum(violations.values())
        status = "🟢 PASS" if total == 0 else "🔴 FAIL"
        detailed = data["output"] if data["output"].strip() else "No complexity violations."

        mapping = {
             "date": datetime.datetime.now().strftime("%Y-%m-%d"),
             "date": datetime.datetime.now().strftime("%Y-%m-%d"),
             "display_grade": grade,
             "grade_color": Grader.get_grade_color(grade),
             "overall_status": status,
             "total_violations": total,
             "top_complex_functions": f"```\n{detailed}\n```",
             "cplx_status": status,
             "cplx_violations": total
        }

        # Generate dynamic module table based on actual violations
        module_table = "| Module | Status | Avg Complexity | Max Complexity | Violations (>10) |\n| :--- | :---: | :---: | :---: | :---: |\n"
        if violations:
            for module, viol_count in sorted(violations.items(), key=lambda x: x[1], reverse=True):
                status = "🟢" if viol_count == 0 else "🔴"
                module_table += f"| **{module}** | {status} | - | - | {viol_count} |\n"
        else:
            module_table += "| **All Modules** | 🟢 | - | - | 0 |\n"
        
        mapping["module_table"] = module_table

        # 3. Render
        self.template_engine.render("complexity_report_template.md", mapping, self.details_dir / "complexity_report.md")

    def _generate_overview(self, results):
        arch = results["architecture"]
        type_ = results["type_safety"]
        cplx = results["complexity"]
        
        mapping = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "overall_status": "🟢 HEALTHY" if all(x["status"] == "PASS" for x in results.values()) else "🟡 ISSUES DETECTED",
            "arch_status": arch["status"],
            "arch_violations": "-",
            "struct_status": "⚪ N/A",
            "struct_violations": "-",
            "type_status": type_["status"],
            "type_violations": type_["violation_count"],
            "cplx_status": cplx["status"],
            "cplx_violations": cplx["violation_count"],
        }
        
        # Calculate overall grade
        sub_grades = [arch.get("grade", "F"), type_.get("grade", "F"), cplx.get("grade", "F")]
        grade = Grader.calculate_overall_grade(sub_grades)
        mapping["display_grade"] = grade
        mapping["grade_color"] = Grader.get_grade_color(grade)
        
        self.template_engine.render("quality_overview_template.md", mapping, self.details_dir / "quality_overview.md")

    def _get_executable(self, name: str) -> str:
        bin_dir = Path(sys.executable).parent
        exe_path = bin_dir / (name + ".exe" if sys.platform == "win32" else name)
        if exe_path.exists(): 
            return str(exe_path)
        which = shutil.which(name)
        if not which:
            logger.warning(f"Executable {name} not found in PATH or Python bin.")
        return which if which else name

    def _run_command(self, command: List[str], cwd: Path = None) -> (str, str, int):
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, cwd=cwd or Path.cwd(), encoding='utf-8', errors='replace'
            )
            return result.stdout, result.stderr, result.returncode
        except Exception as e:
            logger.error(f"Error running command {command}: {e}")
            return "", str(e), -1

    def _run_architecture_check(self):
        logger.info("Running Architecture Check...")
        cmd = [self._get_executable("lint-imports")]
        stdout, stderr, code = self._run_command(cmd)
        return {"tool": "import-linter", "status": "PASS" if code == 0 else "FAIL", "output": stdout + stderr}

    def _run_type_check(self, target: str):
        logger.info("Running Type Check...")
        cmd = [self._get_executable("mypy"), "--strict", target]
        stdout, stderr, code = self._run_command(cmd)
        return {"tool": "mypy", "status": "PASS" if code == 0 else "FAIL", "output": stdout + stderr, "violation_count": stdout.count("error:")}

    def _run_complexity_check(self, target: str):
        logger.info("Running Complexity Check...")
        cmd = [self._get_executable("ruff"), "check", "--select", "C901", target]
        stdout, stderr, code = self._run_command(cmd)
        return {"tool": "ruff", "status": "PASS" if code == 0 else "FAIL", "output": stdout + stderr, "violation_count": stdout.count("C901")}

    def _parse_mypy_output(self, output):
        mod_stats = {}
        cat_stats = {}
        pattern = re.compile(r"([^:]+):.*error:.*\[([^\]]+)\]")
        for line in output.splitlines():
            if "error:" not in line: continue
            match = pattern.search(line)
            if match:
                fpath = match.group(1).replace("\\", "/")
                name = Path(fpath).stem.capitalize()
                parts = fpath.split("/")
                if "src" in parts and "src" in parts:
                    idx = parts.index("src")
                    if idx + 3 < len(parts): name = parts[idx+3].capitalize()
                mod_stats[name] = mod_stats.get(name, 0) + 1
                cat_stats[match.group(2)] = cat_stats.get(match.group(2), 0) + 1
        return mod_stats, cat_stats

    def _parse_ruff_output(self, output):
        mod_stats = {}
        pattern = re.compile(r"([^:]+):.*C901.*complex")
        for line in output.splitlines():
            match = pattern.search(line)
            if match:
                fpath = match.group(1).replace("\\", "/")
                name = Path(fpath).stem.capitalize()
                parts = fpath.split("/")
                if "src" in parts and "src" in parts:
                    idx = parts.index("src")
                    if idx + 3 < len(parts): name = parts[idx+3].capitalize()
                mod_stats[name] = mod_stats.get(name, 0) + 1
        return mod_stats
