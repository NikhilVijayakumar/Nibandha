import json
from pathlib import Path
from typing import Dict, Any, List, TYPE_CHECKING, Optional
import logging
from nibandha.reporting.shared.infrastructure import utils
from nibandha.reporting.shared.rendering.template_engine import TemplateEngine
from nibandha.reporting.shared.domain.protocols.visualization_protocol import VisualizationProvider
from nibandha.reporting.shared.domain.protocols.template_provider_protocol import TemplateProviderProtocol
from nibandha.reporting.shared.infrastructure.visualizers.default_visualizer import DefaultVisualizationProvider
from nibandha.reporting.shared.data.data_builders import UnitDataBuilder
from nibandha.reporting.shared.domain.grading import Grader, GradingThresholds
from nibandha.reporting.shared.domain.reference_models import FigureReference, TableReference, NomenclatureItem

if TYPE_CHECKING:
    from nibandha.reporting.shared.domain.protocols.module_discovery import ModuleDiscoveryProtocol
    from nibandha.reporting.shared.domain.protocols.reference_collector_protocol import ReferenceCollectorProtocol

logger = logging.getLogger("nibandha.reporting.unit")

class UnitReporter:
    def __init__(
        self, 
        output_dir: Path, 
        templates_dir: Path, 
        docs_dir: Path,
        template_engine: Optional[TemplateProviderProtocol] = None,
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
        self.data_builder = UnitDataBuilder()
        self.module_discovery = module_discovery
        self.source_root = source_root
        self.reference_collector = reference_collector

    def generate(self, data: Dict[str, Any], cov_data: Dict[str, Any], timestamp: str, project_name: str = "Project") -> Dict[str, Any]:
        logger.info("Generating Unit Test Report...")
        report_data = self.data_builder.build(data, cov_data, timestamp)
        enriched_data = self._enrich_data_for_template(report_data, data, cov_data)
        enriched_data["project_name"] = project_name
        
        self.template_engine.save_data(enriched_data, self.data_dir / "unit_data.json")
        self.viz_provider.generate_unit_test_charts(enriched_data, self.images_dir)
        logger.debug("Unit charts generated.")

        from nibandha.reporting.shared.constants import (
            PROJECT_ROOT_MARKER, ASSETS_IMAGES_DIR_REL, 
            COLOR_PASS, COLOR_FAIL, COLOR_WARNING, COLOR_NEUTRAL
        )

        target_path = self.details_dir / "03_unit_report.md"
        logger.info(f"Rendering Unit Report to: {target_path}")
        self.template_engine.render(
            "unit_report_template.md",
            enriched_data,
            target_path
        )
        return enriched_data

    def _enrich_data_for_template(self, report_data: Dict[str, Any], original_pytest: Dict[str, Any], original_cov: Dict[str, Any]) -> Dict[str, Any]:
        from nibandha.reporting.shared.constants import (
            PROJECT_ROOT_MARKER, ASSETS_IMAGES_DIR_REL,
            IMG_PATH_UNIT_OUTCOMES, IMG_PATH_UNIT_COVERAGE,
            IMG_PATH_UNIT_DURATIONS, IMG_PATH_UNIT_SLOWEST,
            IMG_PATH_UNIT_MODULE_DURATIONS
        )
        
        logger.debug("Enriching report data with coverage and documentation metrics")
        data = report_data.copy()
        data["total"] = data["total_tests"]
        # Duplicate assignment removed
        data["duration"] = sum(data.get("durations", []))
        
        # Ensure raw tests are available
        data["tests"] = original_pytest.get("tests", [])
        
        prefix = f"{str(self.source_root)}/" if self.source_root else PROJECT_ROOT_MARKER
        all_modules = utils.get_all_modules(self.source_root, self.module_discovery)
        cov_map, total_cov = utils.analyze_coverage(original_cov, package_prefix=prefix, known_modules=all_modules)
        module_results = self._group_results(original_pytest)
        
        # Override data builder coverage with our more accurate calculation
        coverage_rate = total_cov
        data["coverage_rate"] = total_cov

        # Calculate Grade (using accurate coverage)
        pass_rate = data.get("pass_rate", 0)
        grade = Grader.calculate_unit_grade(pass_rate, coverage_rate)
        data["grade"] = grade
        data["grade_color"] = Grader.get_grade_color(grade)
        
        modules_list = []
        
        for mod in sorted(module_results.keys()):
            m_data = module_results[mod]
            cov_val = cov_map.get(mod, 0)
            
            # Grade
            module_pass_rate = (m_data['pass'] / m_data['total'] * 100) if m_data['total'] > 0 else 100
            module_grade = Grader.calculate_unit_grade(module_pass_rate, cov_val)
            grade_color = Grader.get_grade_color(module_grade)
            
            # Tests & Duration
            tests_list = []
            module_duration = 0.0
            if m_data['tests']:
                for t in m_data["tests"]:
                    dur = t.get("call", {}).get("duration", 0) or t.get("setup", {}).get("duration", 0)
                    module_duration += dur
                    tests_list.append({
                        "name": t["nodeid"].split("::")[-1],
                        "outcome": t["outcome"],
                        "icon": "[PASS]" if t["outcome"] == "passed" else "[FAIL]",
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
                "duration": f"{module_duration:.3f}s",
                "duration_val": module_duration,
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
                "icon": "[PASS]",
                "color": "green" if pass_rate >= GradingThresholds.PASS_RATE_TARGET else ("yellow" if pass_rate >= GradingThresholds.PASS_RATE_CRITICAL else "red")
            },
            {
                "title": "Code Coverage",
                "value": f"{coverage_rate:.1f}%",
                "change": "",
                "trend": "neutral",
                "icon": "[COV]",
                "color": "green" if coverage_rate >= GradingThresholds.COVERAGE_TARGET else ("yellow" if coverage_rate >= GradingThresholds.COVERAGE_CRITICAL else "red")
            },
            {
                "title": "Total Tests",
                "value": str(total_tests),
                "change": "",
                "trend": "neutral",
                "icon": "[TEST]",
                "color": "blue"
            },
            {
                "title": "Failed Tests",
                "value": str(failed_tests),
                "change": "",
                "trend": "neutral",
                "icon": "[FAIL]",
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
                 "title": "Module Test Outcomes & Pass Rate Analysis",
                 "path": ASSETS_IMAGES_DIR_REL + IMG_PATH_UNIT_OUTCOMES,
                 "type": "bar_chart",
                 "description": "Visual breakdown of test results including pass rates per module"
             },
             {
                 "id": "fig-unit-2",
                 "title": "Code Coverage Risk Analysis",
                 "path": ASSETS_IMAGES_DIR_REL + IMG_PATH_UNIT_COVERAGE,
                 "type": "bar_chart",
                 "description": "Coverage metrics per module with risk thresholds (50% Critical, 80% Target)"
             },
             {
                 "id": "fig-unit-3",
                 "title": "Test Duration Distribution Analysis",
                 "path": ASSETS_IMAGES_DIR_REL + IMG_PATH_UNIT_DURATIONS,
                 "type": "histogram",
                 "description": "Distribution of test execution times with KDE and outliers"
             },
             {
                 "id": "fig-unit-4",
                 "title": "Performance Bottlenecks: Top 10 Slowest Tests",
                 "path": ASSETS_IMAGES_DIR_REL + IMG_PATH_UNIT_SLOWEST,
                 "type": "bar_chart",
                 "description": "Top 10 slowest unit tests by execution time"
             },
             {
                 "id": "fig-unit-5",
                 "title": "Module execution duration comparison",
                 "path": ASSETS_IMAGES_DIR_REL + IMG_PATH_UNIT_MODULE_DURATIONS,
                 "type": "bar_chart",
                 "description": "Execution time comparison by module"
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
                    definition=nom_data["def"], # type: ignore
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

    def _group_results(self, data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        module_results = self._initialize_module_buckets()
        
        for t in data.get("tests", []):
            mod = self._determine_module_for_test(t)
            self._update_module_stats(module_results, mod, t)
            
        if module_results["Unknown"]["total"] == 0: 
            del module_results["Unknown"]
        return module_results

    def _initialize_module_buckets(self) -> Dict[str, Dict[str, Any]]:
        all_modules = utils.get_all_modules(self.source_root, self.module_discovery)
        buckets: Dict[str, Dict[str, Any]] = {mod: {"total": 0, "pass": 0, "fail": 0, "error": 0, "tests": []} for mod in all_modules}
        buckets["Unknown"] = {"total": 0, "pass": 0, "fail": 0, "error": 0, "tests": []}
        return buckets

    def _determine_module_for_test(self, test_item: Dict[str, Any]) -> str:
        parts = test_item["nodeid"].replace("\\", "/").split("/")
        mod = "Unknown"
        
        if "unit" in parts:
            idx = parts.index("unit")
            if idx + 1 < len(parts): mod = parts[idx + 1].capitalize()
        elif "domain" in parts: 
            idx = parts.index("domain")
            if idx + 1 < len(parts): mod = parts[idx + 1].capitalize()
        
        if mod == "Rotation":
            return "Logging"
        return mod

    def _update_module_stats(self, results: Dict[str, Dict[str, Any]], mod: str, test_item: Dict[str, Any]) -> None:
        if mod not in results:
            results[mod] = {"total": 0, "pass": 0, "fail": 0, "error": 0, "tests": []}
        
        stats = results[mod]
        stats["total"] += 1
        stats["tests"].append(test_item)
        
        if test_item["outcome"] == "passed": 
            stats["pass"] += 1
        elif "error" in test_item.get("keywords", []): 
            stats["error"] += 1
        else: 
            stats["fail"] += 1
