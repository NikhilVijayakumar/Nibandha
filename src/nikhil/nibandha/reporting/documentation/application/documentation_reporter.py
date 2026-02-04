import logging
import datetime
from pathlib import Path
from typing import Dict, Any, List, TYPE_CHECKING, Optional
from ...shared.domain.grading import Grader
from ...shared.rendering.template_engine import TemplateEngine
from ...shared.domain.protocols.visualization_protocol import VisualizationProvider
from ...shared.infrastructure import utils
from ...shared.domain.reference_models import FigureReference, TableReference, NomenclatureItem

if TYPE_CHECKING:
    from ...shared.domain.protocols.module_discovery import ModuleDiscoveryProtocol
    from ...shared.domain.protocols.reference_collector_protocol import ReferenceCollectorProtocol

logger = logging.getLogger("nibandha.reporting.documentation")

class DocumentationReporter:
    def __init__(
        self, 
        output_dir: Path, 
        templates_dir: Path,
        doc_paths: Dict[str, Path],
        template_engine: Optional[TemplateEngine] = None,
        viz_provider: Optional[VisualizationProvider] = None,
        module_discovery: Optional["ModuleDiscoveryProtocol"] = None,
        source_root: Optional[Path] = None,
        reference_collector: Optional["ReferenceCollectorProtocol"] = None
    ):
        self.output_dir = output_dir
        self.templates_dir = templates_dir
        self.doc_paths = doc_paths
        self.reference_collector = reference_collector
        
        self.details_dir = output_dir / "details"
        self.data_dir = output_dir / "assets" / "data" / "documentation"
        self.images_dir = output_dir / "assets" / "images" / "documentation"
        
        self.details_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)

        self.template_engine = template_engine or TemplateEngine(templates_dir)
        self.viz_provider = viz_provider
        self.module_discovery = module_discovery
        self.source_root = source_root
        
    def generate(self, project_root: Path, project_name: str = "Project") -> Dict[str, Any]:
        """Generates the documentation report."""
        logger.info("Generating Documentation Report...")
        
        modules = utils.get_all_modules(self.source_root, self.module_discovery)
        
        # 1. Gather Data
        func_data = self._check_functional(project_root, modules)
        tech_data = self._check_technical(project_root, modules)
        test_data = self._check_test(project_root, modules)
        
        all_data = {
            "functional": func_data,
            "technical": tech_data,
            "test": test_data,
            "modules": modules
        }
        
        # 2. Visualize
        charts = {}
        if self.viz_provider:
             charts = self.viz_provider.generate_documentation_charts(all_data, self.images_dir)
        
        # 3. Render
        self._render_report(all_data, charts, project_name)
        
        return all_data

    def _render_report(self, data: Dict[str, Any], charts: Dict[str, str], project_name: str ="Project") -> None:
        func = data["functional"]
        tech = data["technical"]
        test = data["test"]
        
        # Calculate Grades based on coverage (Percent Documented)
        func_pct = self._calc_pct(func)
        tech_pct = self._calc_pct(tech)
        test_pct = self._calc_pct(test)
        
        func_grade = Grader.calculate_unit_grade(func_pct, 100) # Reusing unit grade logic (Pass% -> Coverage)
        tech_grade = Grader.calculate_unit_grade(tech_pct, 100)
        test_grade = Grader.calculate_unit_grade(test_pct, 100)
        
        overall_grade = Grader.calculate_overall_grade([func_grade, tech_grade, test_grade])
        
        mapping = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "display_grade": overall_grade,
            "grade_color": Grader.get_grade_color(overall_grade),
            "func_grade": func_grade,
            "tech_grade": tech_grade,
            "test_grade": test_grade,
            "func_coverage": f"{func_pct:.1f}",
            "tech_coverage": f"{tech_pct:.1f}",
            "test_coverage": f"{test_pct:.1f}",
            "charts": self._render_charts_section(charts),
            "func_table": self._build_doc_table(func),
            "tech_table": self._build_doc_table(tech),
            "test_table": self._build_test_table(test),
            "missing_section": self._build_missing_section(data),
            "project_name": project_name
        }

        # Register References (Order 10)
        if self.reference_collector:
            self.reference_collector.add_figure(FigureReference(
                id="fig-doc-coverage",
                title="Documentation coverage by category",
                path="../assets/images/documentation/doc_coverage.png",
                type="bar_chart",
                description="Percentage of modules documented across Functional, Technical, and Test categories",
                source_report="documentation",
                report_order=10
            ))
            if charts and "doc_drift" in charts:
                self.reference_collector.add_figure(FigureReference(
                    id="fig-doc-drift",
                    title="Documentation drift analysis",
                    path="../assets/images/documentation/doc_drift.png",
                    type="scatter_chart",
                    description="Age of documentation relative to code changes",
                    source_report="documentation",
                    report_order=10
                ))
            
            self.reference_collector.add_table(TableReference(
                id="table-doc-summary",
                title="Overall documentation grades",
                description="Grades for functional, technical, and test documentation",
                source_report="documentation",
                report_order=10
            ))
            self.reference_collector.add_table(TableReference(
                id="table-func-doc",
                title="Functional documentation status",
                description="Per-module functional documentation status and drift",
                source_report="documentation",
                report_order=10
            ))
        
        self.template_engine.render("documentation_report_template.md", mapping, self.details_dir / "10_documentation_report.md")

    def _calc_pct(self, section_data: Dict[str, Any]) -> float:
        stats = section_data["stats"]
        total = stats["documented"] + stats["missing"]
        return (stats["documented"] / total * 100) if total > 0 else 0

    def _render_charts_section(self, charts: Dict[str, str]) -> str:
        md = ""
        if charts and "doc_coverage" in charts:
            rel_cov = Path(charts['doc_coverage']).name
            img_base = "../assets/images/documentation"
            
            # Figure 1: Coverage
            md += f"![**Figure 1:** Documentation coverage distribution]({img_base}/{rel_cov})\n\n"
            
            # Figure 2: Drift (if exists)
            if "doc_drift" in charts:
                rel_drift = Path(charts['doc_drift']).name
                md += f"![**Figure 2:** Documentation drift analysis]({img_base}/{rel_drift})\n"
        return md

    def _build_doc_table(self, data: Dict[str, Any]) -> str:
        """Build documentation table with grades per module."""
        rows = ""
        for mod, info in data["modules"].items():
            status = "✅ Found" if info["exists"] else "❌ Missing"
            drift = info["drift"] if info["exists"] else "-"
            if isinstance(drift, int) and drift > 90:
                 drift = f"⚠️ {drift}"
            
            # Calculate grade based on existence
            coverage = 100 if info["exists"] else 0
            grade = Grader.calculate_unit_grade(coverage, 100)
            grade_color = Grader.get_grade_color(grade)
            grade_display = f"<span style=\"color:{grade_color}\">{grade}</span>"
            
            rows += f"| {mod} | {status} | {drift} | {grade_display} |\n"
        return rows

    def _build_test_table(self, data: Dict[str, Any]) -> str:
        """Build test documentation table with grades per module."""
        rows = ""
        for mod, info in data["modules"].items():
            unit = "✅" if info["unit_exists"] else "❌"
            e2e = "✅" if info["e2e_exists"] else "❌"
            drift = info["max_drift"]
            if drift == -1: drift = "-"
            
            # Calculate grade based on coverage
            coverage = 0
            if info["unit_exists"]: coverage += 50
            if info["e2e_exists"]: coverage += 50
            grade = Grader.calculate_unit_grade(coverage, 100)
            grade_color = Grader.get_grade_color(grade)
            grade_display = f"<span style=\"color:{grade_color}\">{grade}</span>"
            
            rows += f"| {mod} | {unit} | {e2e} | {drift} | {grade_display} |\n"
        return rows
        
    def _build_missing_section(self, data: Dict[str, Any]) -> str:
        missing = []
        for cat in ["functional", "technical", "test"]:
             for mod, info in data[cat]["modules"].items():
                  if cat == "test":
                       if not info["unit_exists"] and not info["e2e_exists"]:
                           missing.append(f"{mod} (Test)")
                  elif not info["exists"]:
                       missing.append(f"{mod} ({cat.capitalize()})")
        
        if not missing:
            return "All modules are documented! 🎉"
        return ", ".join(missing)

    def _resolve_doc_path(self, root: Path, module: str, category: str) -> Path:
        """Resolves documentation path, checking 'docs/features' then 'docs/modules'."""
        features_path = root / "docs" / "features" / module.lower() / category
        modules_path = root / "docs" / "modules" / module.lower() / category
        
        if features_path.exists():
            return features_path
        return modules_path

    def _check_functional(self, root: Path, modules: List[str]) -> Dict[str, Any]:
        results = {}
        documented = 0
        missing = 0
        drift_map = {}
        
        for mod in modules:
            code_ts = self._get_code_timestamp(root, mod)
            mod_func_dir = self._resolve_doc_path(root, mod, "functional")
            func_path = mod_func_dir / "README.md"
            
            exists = func_path.exists()
            if exists: documented += 1
            else: missing += 1
            
            doc_ts = func_path.stat().st_mtime if exists else 0
            drift = self._calc_drift_days(doc_ts, code_ts) if doc_ts > 0 else -1
            
            results[mod] = {"exists": exists, "drift": drift}
            drift_map[mod] = drift
        
        return {"stats": {"documented": documented, "missing": missing}, "modules": results, "drift_map": drift_map}

    def _check_technical(self, root: Path, modules: List[str]) -> Dict[str, Any]:
        results = {}
        documented = 0
        missing = 0
        drift_map = {}
        
        for mod in modules:
            code_ts = self._get_code_timestamp(root, mod)
            mod_tech_dir = self._resolve_doc_path(root, mod, "technical")
            
            exists = mod_tech_dir.exists() and any(mod_tech_dir.glob("*.md"))
            if exists: documented += 1
            else: missing += 1
            
            doc_ts = self._get_dir_timestamp(mod_tech_dir) if exists else 0
            drift = self._calc_drift_days(doc_ts, code_ts) if doc_ts > 0 else -1
            
            results[mod] = {"exists": exists, "drift": drift}
            drift_map[mod] = drift
        
        return {"stats": {"documented": documented, "missing": missing}, "modules": results, "drift_map": drift_map}

    def _check_test(self, root: Path, modules: List[str]) -> Dict[str, Any]:
        results = {}
        documented = 0
        missing = 0
        drift_map = {}
        
        for mod in modules:
            code_ts = self._get_code_timestamp(root, mod)
            mod_test_dir = self._resolve_doc_path(root, mod, "test")
            
            unit_path = mod_test_dir / "unit_test_scenarios.md"
            e2e_path = mod_test_dir / "e2e_test_scenarios.md"
            unit_path_alt = mod_test_dir / "unit_scenarios.md"
            e2e_path_alt = mod_test_dir / "e2e_scenarios.md"
            
            unit_exists = unit_path.exists() or unit_path_alt.exists()
            e2e_exists = e2e_path.exists() or e2e_path_alt.exists()
            
            unit_ts = 0.0
            if unit_exists:
                unit_ts = float(unit_path.stat().st_mtime if unit_path.exists() else unit_path_alt.stat().st_mtime)
            
            e2e_ts = 0.0
            if e2e_exists:
                e2e_ts = float(e2e_path.stat().st_mtime if e2e_path.exists() else e2e_path_alt.stat().st_mtime)
            
            exists = unit_exists or e2e_exists
            if exists: documented += 1
            else: missing += 1
            
            doc_ts = max(unit_ts, e2e_ts)
            drift = self._calc_drift_days(doc_ts, code_ts) if doc_ts > 0 else -1
            
            results[mod] = {
                "unit_exists": unit_exists, "e2e_exists": e2e_exists, "max_drift": drift
            }
            drift_map[mod] = drift
            
        return {"stats": {"documented": documented, "missing": missing}, "modules": results, "drift_map": drift_map}

    def _scan_generic(self, root: Path, modules: List[str], base_path: Path, suffix: str, is_dir: bool = False) -> None:
        # ... logic as before (not verified used in Generate but seems helper)
        # keeping implementation simple to mirror original
        pass # Skipping re-implementation as it's cleaner to stick to generate logic

    def _get_code_timestamp(self, root: Path, mod_name: str) -> float:
        mod_path = (self.source_root or root / "src") / mod_name.lower()
        if not mod_path.exists(): 
             # Fallback to older default if self.source_root not set/found
             mod_path = root / "src/nikhil/nibandha" / mod_name.lower()
        if not mod_path.exists(): return datetime.datetime.now().timestamp()
        return self._get_dir_timestamp(mod_path)

    def _get_dir_timestamp(self, path: Path) -> float:
        if not path.exists(): return 0.0
        latest = 0.0
        for p in path.rglob("*"):
            if p.is_file():
                latest = max(latest, float(p.stat().st_mtime))
        return latest

    def _calc_drift_days(self, doc_ts: float, code_ts: float) -> int:
        if doc_ts >= code_ts: return 0 
        diff = code_ts - doc_ts
        return int(diff / 86400)
