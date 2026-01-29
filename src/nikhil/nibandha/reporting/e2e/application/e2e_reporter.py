import json
from pathlib import Path
from typing import Dict, Any, List, TYPE_CHECKING, Optional
import logging
from ...shared.infrastructure.visualizers import matplotlib_impl as visualizer
from ...shared.infrastructure import utils
from ...shared.rendering.template_engine import TemplateEngine
from ...shared.domain.protocols.visualization_protocol import VisualizationProvider
from ...shared.infrastructure.visualizers.default_visualizer import DefaultVisualizationProvider
from ...shared.data.data_builders import E2EDataBuilder
from ...shared.domain.grading import Grader
from ...shared.domain.reference_models import FigureReference, TableReference, NomenclatureItem

if TYPE_CHECKING:
    from ...shared.domain.protocols.module_discovery import ModuleDiscoveryProtocol
    from ...shared.domain.protocols.reference_collector_protocol import ReferenceCollectorProtocol

logger = logging.getLogger("nibandha.reporting.e2e")

class E2EReporter:
    def __init__(
        self, 
        output_dir: Path, 
        templates_dir: Path, 
        docs_dir: Path,
        template_engine: Optional[TemplateEngine] = None,
        viz_provider: Optional[VisualizationProvider] = None,
        module_discovery: Optional["ModuleDiscoveryProtocol"] = None,
        source_root: Optional[Path] = None,
        reference_collector: Optional["ReferenceCollectorProtocol"] = None
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
        self.module_discovery = module_discovery
        self.source_root = source_root
        self.reference_collector = reference_collector

    def generate(self, data: Dict[str, Any], timestamp: str, project_name: str = "Project") -> Dict[str, Any]:
        """Generate E2E report using newly architecture."""
        logger.info("Generating E2E Report...")
        
        # 1. Build Data
        report_data = self.data_builder.build(data, timestamp)
        
        # 2. Add formatted Markdown sections (for compatibility with existing template)
        enriched_data = self._enrich_data_for_template(report_data, data)
        enriched_data["project_name"] = project_name
        
        # 3. Save Data
        self.template_engine.save_data(enriched_data, self.data_dir / "e2e_data.json")
        
        # 4. Generate Visualizations
        self.viz_provider.generate_e2e_test_charts(enriched_data, self.images_dir)
        logger.debug("E2E charts generated.")
        
        # 5. Render Template
        target_path = self.details_dir / "04_e2e_report.md"
        logger.info(f"Rendering E2E Report to: {target_path}")
        self.template_engine.render(
            "e2e_report_template.md",
            enriched_data,
            target_path
        )
        return enriched_data

    def _enrich_data_for_template(self, report_data: Dict[str, Any], original_pytest: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich data with markdown tables for the simple template."""
        logger.debug("Enriching E2E data for template")
        data = report_data.copy()
        
        self._enrich_grades(data)
        
        e_tests = original_pytest.get("tests", [])
        module_results = self._group_tests_by_module(e_tests)
        
        data.update(self._generate_tables(module_results, e_tests))
        
        if self.reference_collector:
            self._register_references()
            
        return data

    def _enrich_grades(self, data: Dict[str, Any]) -> None:
        data["total"] = data["total_scenarios"]
        pass_rate = data.get("pass_rate", 0)
        grade = Grader.calculate_e2e_grade(pass_rate)
        data["grade"] = grade
        data["grade_color"] = Grader.get_grade_color(grade)

    def _group_tests_by_module(self, tests: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        # Initialize all modules with default values
        all_modules = utils.get_all_modules(self.source_root, self.module_discovery)
        module_results: Dict[str, Dict[str, Any]] = {mod: {"total": 0, "pass": 0, "fail": 0, "tests": []} for mod in all_modules}
        
        for t in tests:
            mod = self._resolve_test_module(t)
            
            if mod not in module_results:
                # If a test belongs to a module we didn't discover, add it
                module_results[mod] = {"total": 0, "pass": 0, "fail": 0, "tests": []}
                
            module_results[mod]["total"] += 1
            if t["outcome"] == "passed": module_results[mod]["pass"] += 1
            else: module_results[mod]["fail"] += 1
            module_results[mod]["tests"].append(t)
            
        # Clean up 'Other' if empty
        if "Other" in module_results and module_results["Other"]["total"] == 0:
            del module_results["Other"]
        return module_results

    def _resolve_test_module(self, test_item: Dict[str, Any]) -> str:
        parts = test_item["nodeid"].replace("\\", "/").split("/")
        mod = "Other"
        if "e2e" in parts:
            idx = parts.index("e2e")
            if idx + 1 < len(parts):
                mod = parts[idx + 1].capitalize()
        elif "domain" in parts: # Legacy
            idx = parts.index("domain")
            if idx + 1 < len(parts):
                mod = parts[idx + 1].capitalize()
        
        # Remap Rotation -> Logging (same as Unit)
        if mod == "Rotation":
            mod = "Logging"
        return mod

    def _generate_tables(self, module_results: Dict[str, Any], all_tests: List[Dict[str, Any]]) -> Dict[str, Any]:
        mod_table = ""
        det_sections = ""
        
        for mod in sorted(module_results.keys()):
            m_data = module_results[mod]
            m_pass_rate = (m_data["pass"] / m_data["total"] * 100) if m_data["total"] > 0 else 0
            m_grade = Grader.calculate_e2e_grade(m_pass_rate)
            grade_color = Grader.get_grade_color(m_grade)
            grade_display = f'<span style="color:{grade_color}">{m_grade}</span>'
            
            mod_table += f"| {mod} | {m_data['total']} | {m_data['pass']} | {m_data['fail']} | {grade_display} |\n"
            
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
        
        failures = ""
        for t in all_tests:
             if t["outcome"] != "passed":
                longrepr = t.get("longrepr", "No Traceback")
                if isinstance(longrepr, dict): longrepr = json.dumps(longrepr, indent=2)
                failures += f"### {t['nodeid']}\n```\n{longrepr}\n```\n"

        return {
            "module_table": mod_table,
            "detailed_sections": det_sections,
            "failures_section": failures if failures else "*No Failures*"
        }

    def _register_references(self) -> None:
        if not self.reference_collector: return
        # Figures
        self.reference_collector.add_figure(FigureReference(
            id="fig-e2e-status",
            title="E2E test pass/fail status across all scenarios",
            path="../assets/images/e2e_status.png",
            type="bar_chart",
            description="Distribution of pass/fail status across all E2E scenarios",
            source_report="e2e",
            report_order=4
        ))
        self.reference_collector.add_figure(FigureReference(
            id="fig-e2e-durations",
            title="E2E test execution time by scenario",
            path="../assets/images/e2e_durations.png",
            type="histogram",
            description="Execution time distribution for E2E scenarios",
            source_report="e2e",
            report_order=4
        ))
        # Tables
        self.reference_collector.add_table(TableReference(
            id="table-e2e-modules",
            title="E2E test results by module",
            description="Breakdown of test results passing/failing by module",
            source_report="e2e",
            report_order=4
        ))
        self.reference_collector.add_table(TableReference(
            id="table-e2e-failures",
            title="Failed E2E tests requiring investigation",
            description="List of failed tests with traceback snippets",
            source_report="e2e",
            report_order=4
        ))
        # Nomenclature
        self.reference_collector.add_nomenclature(NomenclatureItem(term="E2E Test", definition="An integrated test scenario verifying end-to-end system behavior", source_reports=["e2e"])) # type: ignore
        self.reference_collector.add_nomenclature(NomenclatureItem(term="Scenario", definition="A specific test case or user flow in an E2E test", source_reports=["e2e"])) # type: ignore
        self.reference_collector.add_nomenclature(NomenclatureItem(term="Pass Rate", definition="Percentage of tests that completed successfully without failures", source_reports=["e2e"])) # type: ignore
