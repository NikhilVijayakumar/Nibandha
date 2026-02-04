import shutil
import sys
import subprocess
import re
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, TYPE_CHECKING, Tuple
import logging
from ...shared.domain.grading import Grader
from ...shared.infrastructure.visualizers import matplotlib_impl as visualizer
from ...shared.infrastructure import utils
from ...shared.rendering.template_engine import TemplateEngine
from ...shared.domain.protocols.visualization_protocol import VisualizationProvider
from ...shared.infrastructure.visualizers.default_visualizer import DefaultVisualizationProvider
from ...shared.domain.reference_models import FigureReference, TableReference, NomenclatureItem

if TYPE_CHECKING:
    from ...shared.domain.protocols.reference_collector_protocol import ReferenceCollectorProtocol

logger = logging.getLogger("nibandha.reporting.quality")

class QualityReporter:
    def __init__(
        self, 
        output_dir: Path, 
        templates_dir: Path,
        template_engine: Optional[TemplateEngine] = None,
        viz_provider: Optional[VisualizationProvider] = None,
        reference_collector: Optional["ReferenceCollectorProtocol"] = None,
        source_root: Optional[Path] = None
    ):
        self.output_dir = output_dir
        self.templates_dir = templates_dir
        self.reference_collector = reference_collector
        self.source_root = source_root
        
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
        return results

    def generate(self, results: Dict[str, Any], project_name: str = "Project") -> None:
        """Generates all quality reports using Template Engine."""
        logger.info("Generating Quality Reports (Architecture, Type Safety, Complexity)")
        # Architecture
        self._generate_architecture_report(results["architecture"], project_name)
        # Type Safety
        self._generate_type_safety_report(results["type_safety"], project_name)
        # Complexity
        self._generate_complexity_report(results["complexity"], project_name)

    def _generate_architecture_report(self, data: Dict[str, Any], project_name: str = "Project") -> None:
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
        
        if "cannot find the file" in output_text.lower() or "no such file" in output_text.lower() or ".importlinter" in output_text.lower():
             detailed_violations = (
                 "> [!WARNING]\n"
                 "> **Configuration file `.importlinter` not found**\n\n"
                 "The architecture report requires a configuration file to define your architectural contracts.\n\n"
                 "**To set up:**\n"
                 "1. Create `.importlinter` in your project root\n"
                 "2. Define architectural rules (see Configuration section below)\n"
                 "3. Run the report again\n\n"
                 "Without configuration, this report cannot enforce architectural boundaries."
             )
             status = "⚠️ NOT CONFIGURED"
        elif status == "PASS":
             detailed_violations = "✅ **No violations detected**\n\nAll architectural contracts are being respected."
             status = "🟢 PASS"
        else:
             detailed_violations = f"```\n{output_text}\n```"
             status = "🔴 FAIL"

        mapping = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "display_grade": grade,
            "grade_color": Grader.get_grade_color(grade),
            "overall_status": status,
            "detailed_violations": detailed_violations,
            "module_breakdown": f"## Module Breakdown\nPlease refer to detailed violations.",
            "status": status,
            "arch_status": status,
            "arch_violations": "-",
            # Add placeholders for template keys if they exist
            "struct_status": "N/A", "struct_violations": "N/A",
            "project_name": project_name
        }
        
        if "PASS" in status:
             mapping["module_breakdown"] = (
                "## 📦 Module Breakdown\n\n"
                "| Module | Status | Violations |\n"
                "| :--- | :---: | :---: |\n"
                f"| **Project** | PASS | - |"
            )

        # Register References - Architecture (Order 5)
        if self.reference_collector:
            self.reference_collector.add_figure(FigureReference(
                id="fig-arch-status",
                title="Architecture validation status",
                path="../assets/images/quality/architecture_status.png",
                type="status_badge",
                description="Overall pass/fail status of architectural contracts",
                source_report="architecture",
                report_order=5
            ))
            # No explicit tables worth registering as they are mostly text output

        # 3. Render
        self.template_engine.render("architecture_report_template.md", mapping, self.details_dir / "05_architecture_report.md")

    def _generate_type_safety_report(self, data: Dict[str, Any], project_name: str = "Project") -> None:
        # Grade
        total_errors = data["violation_count"]
        grade = Grader.calculate_quality_grade(total_errors)
        data["grade"] = grade
        
        # 1. Visualize
        enriched_viz_data: Dict[str, Any] = {"errors_by_module": {}, "errors_by_category": {}}
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
            "display_grade": grade,
            "grade_color": Grader.get_grade_color(grade),
            "overall_status": overall_status,
            "total_errors": total_errors,
            "category_table": category_table,
            "detailed_errors": detailed_errors,
            "type_status": overall_status,
            "type_violations": total_errors,
            "project_name": project_name
        }
        
        # Generate dynamic module table with grades (include all modules)
        all_modules = sorted(list(set(utils.get_all_modules(self.source_root) + list(errors_by_module.keys()))))
        module_table = "| Module | Status | Errors | Grade |\n| :--- | :---: | :---: | :---: |\n"
        
        for module in all_modules:
            error_count = errors_by_module.get(module, 0)
            status_icon = "🔴" if error_count > 0 else "🟢"
            module_grade = Grader.calculate_quality_grade(error_count)
            grade_color = Grader.get_grade_color(module_grade)
            module_table += f"| **{module}** | {status_icon} | {error_count} | <span style=\"color:{grade_color}\">{module_grade}</span> |\n"
        
        mapping["module_table"] = module_table

        # Register References - Type Safety (Order 6)
        if self.reference_collector:
            self.reference_collector.add_figure(FigureReference(
                id="fig-type-modules",
                title="Type errors by module",
                path="../assets/images/quality/type_errors_by_module.png",
                type="bar_chart",
                description="Distribution of MyPy type errors across modules",
                source_report="type_safety",
                report_order=6
            ))
            self.reference_collector.add_table(TableReference(
                id="table-type-categories",
                title="Error types breakdown",
                description="Frequency of different type error categories",
                source_report="type_safety",
                report_order=6
            ))
            self.reference_collector.add_table(TableReference(
                id="table-type-modules",
                title="Type safety status by module",
                description="Per-module error counts and grades",
                source_report="type_safety",
                report_order=6
            ))

        # 3. Render
        self.template_engine.render("type_safety_report_template.md", mapping, self.details_dir / "06_type_safety_report.md")

    def _generate_complexity_report(self, data: Dict[str, Any], project_name: str = "Project") -> None:
        # Get violation count from data (already calculated in run_complexity_check)
        total_violations = data["violation_count"]
        grade = Grader.calculate_quality_grade(total_violations)
        data["grade"] = grade

        # 1. Parse output to get module-level breakdown
        violations_by_module = self._parse_ruff_output(data["output"])
        
        # 2. Visualize
        self.viz_provider.generate_complexity_charts({"violations_by_module": violations_by_module}, self.images_dir)
        
        # 3. Determine status based on actual violation count
        status = "🔴 FAIL" if total_violations > 0 else "🟢 PASS"
        detailed = data["output"] if data["output"].strip() else "No complexity violations."

        mapping = {
             "date": datetime.datetime.now().strftime("%Y-%m-%d"),
             "display_grade": grade,
             "grade_color": Grader.get_grade_color(grade),
             "overall_status": status,
             "total_violations": total_violations,
             "top_complex_functions": f"```\n{detailed}\n```",
             "cplx_status": status,
            "cplx_violations": total_violations,
             "project_name": project_name
        }

        # Generate dynamic module table with grades
        all_modules = sorted(list(set(utils.get_all_modules(self.source_root) + list(violations_by_module.keys()))))
        module_table = "| Module | Status | Violations (>10) | Grade |\n| :--- | :---: | :---: | :---: |\n"
        
        for module in all_modules:
            viol_count = violations_by_module.get(module, 0)
            status_icon = "🔴" if viol_count > 0 else "🟢"
            module_grade = Grader.calculate_quality_grade(viol_count)
            grade_color = Grader.get_grade_color(module_grade)
            module_table += f"| **{module}** | {status_icon} | {viol_count} | <span style=\"color:{grade_color}\">{module_grade}</span> |\n"
        
        mapping["module_table"] = module_table

        # Register References - Complexity (Order 7)
        if self.reference_collector:
            self.reference_collector.add_figure(FigureReference(
                id="fig-complexity-dist",
                title="Complexity score distribution",
                path="../assets/images/quality/complexity_distribution.png",
                type="histogram",
                description="Distribution of cyclomatic complexity scores across codebase",
                source_report="complexity",
                report_order=7
            ))
            self.reference_collector.add_table(TableReference(
                id="table-complexity-modules",
                title="Complexity violations by module",
                description="Per-module count of high-complexity functions",
                source_report="complexity",
                report_order=7
            ))

        # 4. Render
        self.template_engine.render("complexity_report_template.md", mapping, self.details_dir / "07_complexity_report.md")

    def _get_executable(self, name: str) -> str:
        bin_dir = Path(sys.executable).parent
        exe_path = bin_dir / (name + ".exe" if sys.platform == "win32" else name)
        if exe_path.exists(): 
            return str(exe_path)
        which = shutil.which(name)
        if not which:
            logger.warning(f"Executable {name} not found in PATH or Python bin.")
        return which if which else name

    def _run_command(self, command: List[str], cwd: Optional[Path] = None) -> Tuple[str, str, int]:
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, cwd=cwd or Path.cwd(), encoding='utf-8', errors='replace'
            )
            return result.stdout, result.stderr, result.returncode
        except Exception as e:
            logger.error(f"Error running command {command}: {e}")
            return "", str(e), -1

    def _run_architecture_check(self) -> Dict[str, Any]:
        logger.info("Running Architecture Check...")
        cmd = [self._get_executable("lint-imports")]
        stdout, stderr, code = self._run_command(cmd)
        return {"tool": "import-linter", "status": "PASS" if code == 0 else "FAIL", "output": stdout + stderr}

    def _run_type_check(self, target: str) -> Dict[str, Any]:
        logger.info("Running Type Check...")
        cmd = [self._get_executable("mypy"), "--strict", target]
        stdout, stderr, code = self._run_command(cmd)
        violation_count = stdout.count("error:")
        # Pass if no violations, even if exit code is non-zero (e.g. config warnings)
        status = "PASS" if violation_count == 0 else "FAIL"
        return {"tool": "mypy", "status": status, "output": stdout + stderr, "violation_count": violation_count}

    def _run_complexity_check(self, target: str) -> Dict[str, Any]:
        logger.info("Running Complexity Check...")
        cmd = [self._get_executable("ruff"), "check", "--select", "C901", target]
        stdout, stderr, code = self._run_command(cmd)
        violation_count = stdout.count("C901")
        # Pass if no violations, even if exit code is non-zero
        status = "PASS" if violation_count == 0 else "FAIL"
        return {"tool": "ruff", "status": status, "output": stdout + stderr, "violation_count": violation_count}

    def _parse_mypy_output(self, output: str) -> Tuple[Dict[str, int], Dict[str, int]]:
        mod_stats: Dict[str, int] = {}
        cat_stats: Dict[str, int] = {}
        pattern = re.compile(r"([^:]+):.*error:.*\[([^\]]+)\]")
        for line in output.splitlines():
            if "error:" not in line: continue
            match = pattern.search(line)
            if match:
                fpath = match.group(1).replace("\\", "/")
                name = utils.extract_module_name(fpath, self.source_root)
                mod_stats[name] = mod_stats.get(name, 0) + 1
                cat_stats[match.group(2)] = cat_stats.get(match.group(2), 0) + 1
        return mod_stats, cat_stats

    def _parse_ruff_output(self, output: str) -> Dict[str, int]:
        """Parse ruff C901 complexity output to extract violations per module."""
        mod_stats: Dict[str, int] = {}
        
        for line in output.splitlines():
            # Ruff format: "  --> src/nikhil/nibandha/MODULE/...path.py:244:9"
            if '-->' in line and 'src' in line:
                # Extract file path from line
                match = re.search(r'-->\s+(.+?):\d+', line)
                if match:
                    file_path = match.group(1)
                    module = utils.extract_module_name(file_path, self.source_root)
                    mod_stats[module] = mod_stats.get(module, 0) + 1
        
        return mod_stats
