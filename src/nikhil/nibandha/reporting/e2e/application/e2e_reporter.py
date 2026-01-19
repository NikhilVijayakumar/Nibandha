import json
from pathlib import Path
from typing import Dict, Any, List
import logging
from ...shared.infrastructure.visualizers import matplotlib_impl as visualizer
from ...shared.infrastructure import utils
from ...shared.rendering.template_engine import TemplateEngine
from ...shared.domain.protocols.visualization_protocol import VisualizationProvider
from ...shared.infrastructure.visualizers.default_visualizer import DefaultVisualizationProvider
from ...shared.data.data_builders import E2EDataBuilder
from ...shared.domain.grading import Grader

logger = logging.getLogger("nibandha.reporting.e2e")

class E2EReporter:
    def __init__(
        self, 
        output_dir: Path, 
        templates_dir: Path, 
        docs_dir: Path,
        template_engine: TemplateEngine = None,
        viz_provider: VisualizationProvider = None
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
        self.data_builder = E2EDataBuilder()

    def generate(self, data: Dict[str, Any], timestamp: str):
        """Generate E2E report using newly architecture."""
        logger.info("Generating E2E Report...")
        
        # 1. Build Data
        report_data = self.data_builder.build(data, timestamp)
        
        # 2. Add formatted Markdown sections (for compatibility with existing template)
        enriched_data = self._enrich_data_for_template(report_data, data)
        
        # 3. Save Data
        self.template_engine.save_data(enriched_data, self.data_dir / "e2e_data.json")
        
        # 4. Generate Visualizations
        self.viz_provider.generate_e2e_test_charts(enriched_data, self.images_dir)
        logger.debug("E2E charts generated.")
        
        # 5. Render Template
        target_path = self.details_dir / "e2e_report.md"
        logger.info(f"Rendering E2E Report to: {target_path}")
        self.template_engine.render(
            "e2e_report_template.md",
            enriched_data,
            target_path
        )
        return enriched_data

    def _enrich_data_for_template(self, report_data: Dict, original_pytest: Dict) -> Dict:
        """Enrich data with markdown tables for the simple template."""
        logger.debug("Enriching E2E data for template")
        data = report_data.copy()
        data["total"] = data["total_scenarios"]
        
        # Calculate Grade
        pass_rate = data.get("pass_rate", 0)
        grade = Grader.calculate_e2e_grade(pass_rate)
        data["grade"] = grade
        data["grade_color"] = Grader.get_grade_color(grade)
        
        # Group logic (Legacy)
        e_tests = original_pytest.get("tests", [])
        module_results = {}
        for t in e_tests:
            parts = t["nodeid"].replace("\\", "/").split("/")
            mod = "Other"
            if "e2e" in parts:
                idx = parts.index("e2e")
                if idx + 1 < len(parts):
                    mod = parts[idx + 1].capitalize()
            elif "domain" in parts: # Legacy
                idx = parts.index("domain")
                if idx + 1 < len(parts):
                    mod = parts[idx + 1].capitalize()
            
            if mod not in module_results:
                module_results[mod] = {"total": 0, "pass": 0, "fail": 0, "tests": []}
                
            module_results[mod]["total"] += 1
            if t["outcome"] == "passed": module_results[mod]["pass"] += 1
            else: module_results[mod]["fail"] += 1
            module_results[mod]["tests"].append(t)

        mod_table = ""
        det_sections = ""
        for mod in sorted(module_results.keys()):
            m_data = module_results[mod]
            mod_table += f"| {mod} | {m_data['total']} | {m_data['pass']} | {m_data['fail']} |\n"
            
            det_sections += f"### Module: {mod}\n\n"
            if m_data['tests']:
                det_sections += "| Scenario | Status | Duration |\n| --- | :---: | :---: |\n"
                for t in m_data["tests"]:
                    icon = "✅" if t["outcome"] == "passed" else "❌"
                    full_name = t["nodeid"].split("::")[-1]
                    dur = t.get("call", {}).get("duration", 0) or t.get("setup", {}).get("duration", 0)
                    det_sections += f"| {full_name} | {icon} | {dur:.3f}s |\n"
                det_sections += "\n"
            else:
                det_sections += "*No scenarios executed.*\n\n"
        
        data["module_table"] = mod_table
        data["detailed_sections"] = det_sections
        
        failures = ""
        for t in e_tests:
             if t["outcome"] != "passed":
                longrepr = t.get("longrepr", "No Traceback")
                if isinstance(longrepr, dict): longrepr = json.dumps(longrepr, indent=2)
                failures += f"### {t['nodeid']}\n```\n{longrepr}\n```\n"

        data["failures_section"] = failures if failures else "*No Failures*"
        return data
