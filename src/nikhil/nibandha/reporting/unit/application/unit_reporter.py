import json
from pathlib import Path
from typing import Dict, Any, List, TYPE_CHECKING, Optional
import logging
from ...shared.infrastructure.visualizers import matplotlib_impl as visualizer 
from ...shared.infrastructure import utils
from ...shared.rendering.template_engine import TemplateEngine
from ...shared.domain.protocols.visualization_protocol import VisualizationProvider
from ...shared.infrastructure.visualizers.default_visualizer import DefaultVisualizationProvider
from ...shared.data.data_builders import UnitDataBuilder
from ...shared.domain.grading import Grader
from ...shared.domain.reference_models import FigureReference, TableReference, NomenclatureItem

if TYPE_CHECKING:
    from ...shared.domain.protocols.module_discovery import ModuleDiscoveryProtocol
    from ...shared.domain.protocols.reference_collector_protocol import ReferenceCollectorProtocol

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
        source_root: Path = None,
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
        self.data_builder = UnitDataBuilder()
        self.module_discovery = module_discovery
        self.source_root = source_root
        self.reference_collector = reference_collector

    def generate(self, data: Dict[str, Any], cov_data: Dict[str, Any], timestamp: str, project_name: str = "Project"):
        logger.info("Generating Unit Test Report...")
        report_data = self.data_builder.build(data, cov_data, timestamp)
        enriched_data = self._enrich_data_for_template(report_data, data, cov_data)
        enriched_data["project_name"] = project_name
        
        self.template_engine.save_data(enriched_data, self.data_dir / "unit_data.json")
        self.viz_provider.generate_unit_test_charts(enriched_data, self.images_dir)
        logger.debug("Unit charts generated.")

        target_path = self.details_dir / "03_unit_report.md"
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
        
        prefix = f"{str(self.source_root)}/" if self.source_root else "src/"
        all_modules = utils.get_all_modules(self.source_root, self.module_discovery)
        cov_map, total_cov = utils.analyze_coverage(original_cov, package_prefix=prefix, known_modules=all_modules)
        module_results = self._group_results(original_pytest)
        
        # Override data builder coverage with our more accurate calculation
        coverage_rate = total_cov
        data["coverage_rate"] = total_cov
        
        modules_list = []
        
        for mod in sorted(module_results.keys()):
            m_data = module_results[mod]
            cov_val = cov_map.get(mod, 0)
            
            # Grade
            module_pass_rate = (m_data['pass'] / m_data['total'] * 100) if m_data['total'] > 0 else 100
            module_grade = Grader.calculate_unit_grade(module_pass_rate, cov_val)
            grade_color = "red" if module_grade in ["D", "F"] else ("orange" if module_grade == "C" else "green")
            
            # Tests
            tests_list = []
            if m_data['tests']:
                for t in m_data["tests"]:
                    dur = t.get("call", {}).get("duration", 0) or t.get("setup", {}).get("duration", 0)
                    tests_list.append({
                        "name": t["nodeid"].split("::")[-1],
                        "outcome": t["outcome"],
                        "icon": "✅" if t["outcome"] == "passed" else "❌",
                        "duration": f"{dur:.3f}s"
                    })

            modules_list.append({
                "name": mod,
                "total": m_data['total'],
                "passed": m_data['pass'],
                "failed": m_data['fail'] + m_data['error'],
                "coverage": f"{cov_val:.1f}%",
                "coverage_val": cov_val,
                "grade": module_grade,
                "grade_color": grade_color,
                "tests": tests_list,
                "doc_content": utils.get_module_doc(self.docs_dir, mod, "unit")
            })
        
        data["modules"] = modules_list
        
        # NEW: Metrics Cards for dashboard
        total_tests = data.get("total_tests", 0)
        passed_tests = data.get("passed", 0)
        failed_tests = data.get("failed", 0)
        pass_rate = data.get("pass_rate", 0)
        # coverage_rate already updated above
        
        data["metrics_cards"] = [
            {
                "title": "Test Pass Rate",
                "value": f"{pass_rate:.1f}%",
                "change": "",  # Can add trend calculation later
                "trend": "neutral",
                "icon": "✓",
                "color": "green" if pass_rate >= 90 else ("yellow" if pass_rate >= 70 else "red")
            },
            {
                "title": "Code Coverage",
                "value": f"{coverage_rate:.1f}%",
                "change": "",
                "trend": "neutral",
                "icon": "📊",
                "color": "green" if coverage_rate >= 80 else ("yellow" if coverage_rate >= 60 else "red")
            },
            {
                "title": "Total Tests",
                "value": str(total_tests),
                "change": "",
                "trend": "neutral",
                "icon": "🧪",
                "color": "blue"
            },
            {
                "title": "Failed Tests",
                "value": str(failed_tests),
                "change": "",
                "trend": "neutral",
                "icon": "❌",
                "color": "red" if failed_tests > 0 else "green"
            }
        ]
        
        # Lists for LoT and LoF with enhanced metadata
        tables_list = [
             {
                 "id": "table-unit-1",
                 "title": "Project-level unit test metrics",
                 "description": "Overall test statistics and coverage"
             },
             {
                 "id": "table-unit-2",
                 "title": "Per-module unit test results",
                 "description": "Detailed breakdown by module with grades"
             },
             {
                 "id": "table-unit-3",
                 "title": "List of failed tests requiring attention",
                 "description": "Tests that need immediate fixing"
             }
        ]
        figures_list = [
             {
                 "id": "fig-unit-1",
                 "title": "Test pass/fail distribution across all modules",
                 "path": "../assets/images/unit_outcomes.png",
                 "type": "bar_chart",
                 "description": "Visual breakdown of test results"
             },
             {
                 "id": "fig-unit-2",
                 "title": "Code coverage percentage by module",
                 "path": "../assets/images/unit_coverage.png",
                 "type": "bar_chart",
                 "description": "Coverage metrics per module"
             },
             {
                 "id": "fig-unit-3",
                 "title": "Test execution time distribution",
                 "path": "../assets/images/unit_durations.png",
                 "type": "histogram",
                 "description": "Distribution of test execution times"
             }
        ]
        
        # Nomenclature sorted alphabetically
        nomenclature_items = [
            {"term": "Unit Test", "def": "An automated test that validates a single component or function in isolation"},
            {"term": "Test Suite", "def": "A collection of related unit tests"},
            {"term": "Assertion", "def": "A statement that validates expected behavior (if it fails, the test fails)"},
            {"term": "Pass Rate", "def": "Percentage of tests that completed successfully without failures"},
            {"term": "Code Coverage", "def": "Percentage of code lines executed during test runs"},
            {"term": "Test Duration", "def": "Time taken for a test or suite to complete"},
            {"term": "Fixture", "def": "Setup code or data used to prepare the testing environment"}
        ]
        
        # Register with global collector if available
        if self.reference_collector:
            for fig_data in figures_list:
                self.reference_collector.add_figure(FigureReference(
                    id=fig_data["id"],
                    title=fig_data["title"],
                    path=fig_data["path"],
                    type=fig_data["type"],
                    description=fig_data["description"],
                    source_report="unit",
                    report_order=3  # Unit tests = report module 3
                ))
            
            for tab_data in tables_list:
                self.reference_collector.add_table(TableReference(
                    id=tab_data["id"],
                    title=tab_data["title"],
                    description=tab_data["description"],
                    source_report="unit",
                    report_order=3  # Unit tests = report module 3
                ))
            
            for nom_data in nomenclature_items:
                self.reference_collector.add_nomenclature(NomenclatureItem(
                    term=nom_data["term"],
                    definition=nom_data["def"],
                    source_reports=["unit"]
                ))
            
            logger.debug("Registered unit test references with global collector")
        else:
            # Fallback: add to template data for backward compatibility
            data["figures"] = figures_list
            data["tables"] = tables_list
            data["nomenclature"] = sorted(nomenclature_items, key=lambda x: x["term"])
        
        # Legacy support (optional, can be removed if template updated)
        data["detailed_sections"] = "" 
        data["module_table"] = ""
        data["failures_section"] = "" 
        
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
