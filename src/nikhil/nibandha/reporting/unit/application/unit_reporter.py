import json
from pathlib import Path
from typing import Dict, Any, List, TYPE_CHECKING
import logging
from ...shared.infrastructure.visualizers import matplotlib_impl as visualizer 
from ...shared.infrastructure import utils
from ...shared.rendering.template_engine import TemplateEngine
from ...shared.domain.protocols.visualization_protocol import VisualizationProvider
from ...shared.infrastructure.visualizers.default_visualizer import DefaultVisualizationProvider
from ...shared.data.data_builders import UnitDataBuilder
from ...shared.domain.grading import Grader

if TYPE_CHECKING:
    from ...shared.domain.protocols.module_discovery import ModuleDiscoveryProtocol

logger = logging.getLogger("nibandha.reporting.unit")

class UnitReporter:
    def __init__(
        self, 
        output_dir: Path, 
        templates_dir: Path, 
        docs_dir: Path,
        template_engine: TemplateEngine = None,
        viz_provider: VisualizationProvider = None,
        module_discovery: "ModuleDiscoveryProtocol" = None,
        source_root: Path = None
    ):
        self.output_dir = output_dir
        self.templates_dir = templates_dir
        self.docs_dir = docs_dir
        self.details_dir = output_dir / "details"
        self.data_dir = output_dir / "assets" / "data"
        self.images_dir = output_dir / "assets" / "images"
        
        self.details_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)

        self.template_engine = template_engine or TemplateEngine(templates_dir)
        self.viz_provider = viz_provider or DefaultVisualizationProvider()
        self.data_builder = UnitDataBuilder()
        self.module_discovery = module_discovery
        self.source_root = source_root

    def generate(self, data: Dict[str, Any], cov_data: Dict[str, Any], timestamp: str):
        logger.info("Generating Unit Test Report...")
        report_data = self.data_builder.build(data, cov_data, timestamp)
        enriched_data = self._enrich_data_for_template(report_data, data, cov_data)
        
        self.template_engine.save_data(enriched_data, self.data_dir / "unit_data.json")
        self.viz_provider.generate_unit_test_charts(enriched_data, self.images_dir)
        logger.debug("Unit charts generated.")

        target_path = self.details_dir / "unit_report.md"
        logger.info(f"Rendering Unit Report to: {target_path}")
        self.template_engine.render(
            "unit_report_template.md",
            enriched_data,
            target_path
        )
        return enriched_data

    def _enrich_data_for_template(self, report_data: Dict, original_pytest: Dict, original_cov: Dict) -> Dict:
        logger.debug("Enriching report data with coverage and documentation metrics")
        data = report_data.copy()
        data["total"] = data["total_tests"]
        data["total"] = data["total_tests"]
        data["duration"] = sum(data.get("durations", []))
        
        # Calculate Grade
        pass_rate = data.get("pass_rate", 0)
        coverage_rate = data.get("coverage_rate", 0) # Assuming this key exists from DataBuilder
        grade = Grader.calculate_unit_grade(pass_rate, coverage_rate)
        data["grade"] = grade
        data["grade_color"] = Grader.get_grade_color(grade)
        
        cov_map, _ = utils.analyze_coverage(original_cov)
        module_results = self._group_results(original_pytest)
        
        mod_table = ""
        det_sections = ""
        for mod in sorted(module_results.keys()):
            m_data = module_results[mod]
            cov_val = cov_map.get(mod, 0)
            cov_str = f"{cov_val:.1f}%"
            if cov_val < 50 and m_data['total'] > 0:
                cov_str = f"🔴 {cov_str}"
            elif cov_val > 80:
                cov_str = f"🟢 {cov_str}"
            
            # Calculate module-level grade based on pass rate and coverage
            module_pass_rate = (m_data['pass'] / m_data['total'] * 100) if m_data['total'] > 0 else 100
            module_grade = Grader.calculate_unit_grade(module_pass_rate, cov_val)
            grade_color = "red" if module_grade in ["D", "F"] else ("orange" if module_grade == "C" else "green")
            grade_display = f"<span style=\"color:{grade_color}\">{module_grade}</span>"
            
            mod_table += f"| {mod} | {m_data['total']} | {m_data['pass']} | {m_data['fail'] + m_data['error']} | {cov_str} | {grade_display} |\n"
            
            det_sections += f"### Module: {mod}\n\n#### Documentation Scenarios\n\n"
            det_sections += utils.get_module_doc(self.docs_dir, mod, "unit") + "\n\n"
            
            if m_data['tests']:
                det_sections += "#### Execution Results\n\n| Test Case | Status | Duration |\n| --- | :---: | :---: |\n"
                for t in m_data["tests"]:
                    icon = "✅" if t["outcome"] == "passed" else "❌"
                    clean_name = t["nodeid"].split("::")[-1]
                    dur = t.get("call", {}).get("duration", 0) or t.get("setup", {}).get("duration", 0)
                    det_sections += f"| {clean_name} | {icon} | {dur:.3f}s |\n"
                det_sections += "\n"
            else:
                det_sections += "*No tests executed for this module.*\n\n"
        
        data["module_table"] = mod_table
        data["detailed_sections"] = det_sections
        
        failures_md = ""
        for failure in data.get("failures", []):
             failures_md += f"### {failure['test_name']}\n```\n{failure['traceback']}\n```\n"
        data["failures_section"] = failures_md if failures_md else "*No Failures*"
        
        return data

    def _group_results(self, data):
        # Helper to group by module
        all_modules = utils.get_all_modules(self.source_root, self.module_discovery)
        module_results = {mod: {"total": 0, "pass": 0, "fail": 0, "error": 0, "tests": []} for mod in all_modules}
        module_results["Unknown"] = {"total": 0, "pass": 0, "fail": 0, "error": 0, "tests": []}
        
        for t in data.get("tests", []):
            parts = t["nodeid"].replace("\\", "/").split("/")
            mod = "Unknown"
            if "unit" in parts and "unit" in parts:
                idx = parts.index("unit")
                if idx + 1 < len(parts): mod = parts[idx + 1].capitalize()
            elif "domain" in parts: 
                idx = parts.index("domain")
                if idx + 1 < len(parts): mod = parts[idx + 1].capitalize()
            
            # Remap Rotation -> Logging
            if mod == "Rotation":
                mod = "Logging"
            
            if mod not in module_results:
                module_results[mod] = {"total": 0, "pass": 0, "fail": 0, "error": 0, "tests": []}
            
            module_results[mod]["total"] += 1
            if t["outcome"] == "passed": module_results[mod]["pass"] += 1
            elif "error" in t.get("keywords", []): module_results[mod]["error"] += 1
            else: module_results[mod]["fail"] += 1
            module_results[mod]["tests"].append(t)
            
        if module_results["Unknown"]["total"] == 0: del module_results["Unknown"]
        return module_results
