import logging
import datetime
from pathlib import Path
from typing import Dict, Any, List, TYPE_CHECKING
from ...shared.domain.grading import Grader
from ...shared.rendering.template_engine import TemplateEngine
from ...shared.domain.protocols.visualization_protocol import VisualizationProvider
from ...shared.infrastructure import utils

if TYPE_CHECKING:
    from ...shared.domain.protocols.module_discovery import ModuleDiscoveryProtocol

logger = logging.getLogger("nibandha.reporting.documentation")

class DocumentationReporter:
    def __init__(
        self, 
        output_dir: Path, 
        templates_dir: Path,
        doc_paths: Dict[str, Path],
        template_engine: TemplateEngine = None,
        viz_provider: VisualizationProvider = None,
        module_discovery: "ModuleDiscoveryProtocol" = None,
        source_root: Path = None
    ):
        self.output_dir = output_dir
        self.templates_dir = templates_dir
        self.doc_paths = doc_paths
        
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
        
    def generate(self, project_root: Path):
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
        input_viz_data = all_data # or transform if needed
        charts = {}
        if self.viz_provider:
             charts = self.viz_provider.generate_documentation_charts(all_data, self.images_dir)
        
        # 3. Render
        self._render_report(all_data, charts)
        
        return all_data

    def _render_report(self, data, charts):
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
            "missing_section": self._build_missing_section(data)
        }
        
        self.template_engine.render("documentation_report_template.md", mapping, self.details_dir / "documentation_report.md")

    def _calc_pct(self, section_data):
        stats = section_data["stats"]
        total = stats["documented"] + stats["missing"]
        return (stats["documented"] / total * 100) if total > 0 else 0

    def _render_charts_section(self, charts):
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

    def _build_doc_table(self, data):
        """Build documentation table with grades per module."""
        rows = ""
        for mod, info in data["modules"].items():
            status = "✅ Found" if info["exists"] else "❌ Missing"
            drift = info["drift"] if info["exists"] else "-"
            if isinstance(drift, int) and drift > 90:
                 drift = f"⚠️ {drift}"
            
            # Calculate grade based on existence (100% if exists, 0% if missing)
            coverage = 100 if info["exists"] else 0
            grade = Grader.calculate_unit_grade(coverage, 100)  # Reuse unit grading
            grade_color = "red" if grade in ["D", "F"] else ("orange" if grade == "C" else "green")
            grade_display = f"<span style=\"color:{grade_color}\">{grade}</span>"
            
            rows += f"| {mod} | {status} | {drift} | {grade_display} |\n"
        return rows

    def _build_test_table(self, data):
        """Build test documentation table with grades per module."""
        rows = ""
        for mod, info in data["modules"].items():
            unit = "✅" if info["unit_exists"] else "❌"
            e2e = "✅" if info["e2e_exists"] else "❌"
            drift = info["max_drift"]
            if drift == -1: drift = "-"
            
            # Calculate grade based on test doc coverage
            coverage = 0
            if info["unit_exists"]: coverage += 50
            if info["e2e_exists"]: coverage += 50
            grade = Grader.calculate_unit_grade(coverage, 100)
            grade_color = "red" if grade in ["D", "F"] else ("orange" if grade == "C" else "green")
            grade_display = f"<span style=\"color:{grade_color}\">{grade}</span>"
            
            rows += f"| {mod} | {unit} | {e2e} | {drift} | {grade_display} |\n"
        return rows
        
    def _build_missing_section(self, data):
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

    def _check_functional(self, root, modules):
        # NEW: docs/modules/{mod}/functional/README.md
        results = {}
        documented = 0
        missing = 0
        drift_map = {}
        
        for mod in modules:
            code_ts = self._get_code_timestamp(root, mod)
            
            # New path: docs/modules/{module}/functional/README.md
            mod_func_dir = root / "docs" / "modules" / mod.lower() / "functional"
            func_path = mod_func_dir / "README.md"
            
            exists = func_path.exists()
            if exists: documented += 1
            else: missing += 1
            
            doc_ts = func_path.stat().st_mtime if exists else 0
            drift = self._calc_drift_days(doc_ts, code_ts) if doc_ts > 0 else -1
            
            results[mod] = {"exists": exists, "drift": drift}
            drift_map[mod] = drift
        
        return {"stats": {"documented": documented, "missing": missing}, "modules": results, "drift_map": drift_map}

    def _check_technical(self, root, modules):
        # NEW: docs/modules/{mod}/technical/*.md
        results = {}
        documented = 0
        missing = 0
        drift_map = {}
        
        for mod in modules:
            code_ts = self._get_code_timestamp(root, mod)
            
            # New path: docs/modules/{module}/technical/
            mod_tech_dir = root / "docs" / "modules" / mod.lower() / "technical"
            
            # Check if any .md files exist in technical directory
            exists = mod_tech_dir.exists() and any(mod_tech_dir.glob("*.md"))
            if exists: documented += 1
            else: missing += 1
            
            doc_ts = self._get_dir_timestamp(mod_tech_dir) if exists else 0
            drift = self._calc_drift_days(doc_ts, code_ts) if doc_ts > 0 else -1
            
            results[mod] = {"exists": exists, "drift": drift}
            drift_map[mod] = drift
        
        return {"stats": {"documented": documented, "missing": missing}, "modules": results, "drift_map": drift_map}

    def _check_test(self, root, modules):
        # NEW: docs/modules/{mod}/test/unit_scenarios.md and e2e_scenarios.md
        results = {}
        documented = 0
        missing = 0
        drift_map = {}
        
        for mod in modules:
            # Code Timestamp
            code_ts = self._get_code_timestamp(root, mod)
            
            # New path: docs/modules/{module}/test/
            mod_test_dir = root / "docs" / "modules" / mod.lower() / "test"
            
            # Check for various test scenario files
            unit_path = mod_test_dir / "unit_test_scenarios.md"
            e2e_path = mod_test_dir / "e2e_test_scenarios.md"
            
            # Also check for old naming (unit_scenarios.md)
            unit_path_alt = mod_test_dir / "unit_scenarios.md"
            e2e_path_alt = mod_test_dir / "e2e_scenarios.md"
            
            unit_exists = unit_path.exists() or unit_path_alt.exists()
            e2e_exists = e2e_path.exists() or e2e_path_alt.exists()
            
            unit_ts = 0
            if unit_exists:
                unit_ts = unit_path.stat().st_mtime if unit_path.exists() else unit_path_alt.stat().st_mtime
            
            e2e_ts = 0
            if e2e_exists:
                e2e_ts = e2e_path.stat().st_mtime if e2e_path.exists() else e2e_path_alt.stat().st_mtime
            
            exists = unit_exists or e2e_exists
            if exists: documented += 1
            else: missing += 1
            
            # Drift (Max of unit/e2e vs code)
            doc_ts = max(unit_ts, e2e_ts)
            drift = self._calc_drift_days(doc_ts, code_ts) if doc_ts > 0 else -1
            
            results[mod] = {
                "unit_exists": unit_exists, "e2e_exists": e2e_exists, "max_drift": drift
            }
            drift_map[mod] = drift
            
        return {"stats": {"documented": documented, "missing": missing}, "modules": results, "drift_map": drift_map}


    def _scan_generic(self, root, modules, base_path, suffix, is_dir=False):
        results = {}
        documented = 0
        missing = 0
        drift_map = {}
        
        for mod in modules:
            code_ts = self._get_code_timestamp(root, mod)
            
            if is_dir:
                target = base_path / mod.lower() / suffix
            else:
                target = base_path / f"{mod.lower()}{suffix}"
            
            exists = target.exists()
            if exists: 
                documented += 1
                doc_ts = target.stat().st_mtime
                drift = self._calc_drift_days(doc_ts, code_ts)
            else: 
                missing += 1
                drift = -1
                
            results[mod] = {"exists": exists, "drift": drift}
            drift_map[mod] = drift
            
        return {"stats": {"documented": documented, "missing": missing}, "modules": results, "drift_map": drift_map}

    def _get_code_timestamp(self, root, mod_name):
        # src/nikhil/nibandha/{mod}/...
        # Rough calc: max mtime of files in that module
        mod_path = root / "src/nikhil/nibandha" / mod_name.lower()
        if not mod_path.exists(): return datetime.datetime.now().timestamp()
        
        return self._get_dir_timestamp(mod_path)

    def _get_dir_timestamp(self, path):
        if not path.exists(): return 0
        latest = 0
        for p in path.rglob("*"):
            if p.is_file():
                latest = max(latest, p.stat().st_mtime)
        return latest

    def _calc_drift_days(self, doc_ts, code_ts):
        if doc_ts >= code_ts: return 0 
        diff = code_ts - doc_ts
        return int(diff / 86400) # seconds to days
