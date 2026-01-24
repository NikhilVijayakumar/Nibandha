import logging
import datetime
from pathlib import Path
from typing import Dict, Any, List
from ...shared.domain.grading import Grader
from ...shared.rendering.template_engine import TemplateEngine
from ...shared.domain.protocols.visualization_protocol import VisualizationProvider
from ...shared.infrastructure import utils

logger = logging.getLogger("nibandha.reporting.documentation")

class DocumentationReporter:
    def __init__(
        self, 
        output_dir: Path, 
        templates_dir: Path,
        doc_paths: Dict[str, Path],
        template_engine: TemplateEngine = None,
        viz_provider: VisualizationProvider = None
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
        
    def generate(self, project_root: Path):
        """Generates the documentation report."""
        logger.info("Generating Documentation Report...")
        
        modules = utils.get_all_modules()
        
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
        if "doc_coverage" in charts:
            # We need responsive path or absolute? Existing reports use relative to output dir often.
            # But here let's use the path string relative to details dir if possible, or just absolute for now.
            # The template engine usually handles paths if set up right, but here we passed absolute paths.
            # Let's just assume the user reads markdown locally.
            rel_cov = Path(charts['doc_coverage']).name
            rel_drift = Path(charts['doc_drift']).name
            # In 'details/', the images are in '../assets/images/documentation/'
            img_base = "../assets/images/documentation"
            md += f"![Coverage]({img_base}/{rel_cov})\n"
            md += f"![Drift]({img_base}/{rel_drift})\n"
        return md

    def _build_doc_table(self, data):
        rows = ""
        for mod, info in data["modules"].items():
            status = "✅ Found" if info["exists"] else "❌ Missing"
            drift = info["drift"] if info["exists"] else "-"
            if isinstance(drift, int) and drift > 90:
                 drift = f"⚠️ {drift}"
            rows += f"| {mod} | {status} | {drift} |\n"
        return rows

    def _build_test_table(self, data):
        rows = ""
        for mod, info in data["modules"].items():
            unit = "✅" if info["unit_exists"] else "❌"
            e2e = "✅" if info["e2e_exists"] else "❌"
            drift = info["max_drift"]
            if drift == -1: drift = "-"
            rows += f"| {mod} | {unit} | {e2e} | {drift} |\n"
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
        # docs/modules/{mod}/README.md
        base = root / self.doc_paths["functional"]
        return self._scan_generic(root, modules, base, "README.md", is_dir=True)

    def _check_technical(self, root, modules):
        # docs/technical/{mod}.md
        base = root / self.doc_paths["technical"]
        return self._scan_generic(root, modules, base, ".md", is_dir=False)

    def _check_test(self, root, modules):
        # docs/test/unit/{mod}/... and docs/test/e2e/{mod}/...
        # Just check if ANY file exists there
        unit_base = root / self.doc_paths["test"] / "unit"
        e2e_base = root / self.doc_paths["test"] / "e2e"
        
        results = {}
        documented = 0
        missing = 0
        drift_map = {}
        
        for mod in modules:
            # Code Timestamp
            code_ts = self._get_code_timestamp(root, mod)
            
            # Unit
            unit_path = unit_base / mod.lower()
            unit_exists = unit_path.exists() and any(unit_path.iterdir())
            unit_ts = self._get_dir_timestamp(unit_path) if unit_exists else 0
            
            # E2E
            e2e_path = e2e_base / mod.lower()
            e2e_exists = e2e_path.exists() and any(e2e_path.iterdir())
            e2e_ts = self._get_dir_timestamp(e2e_path) if e2e_exists else 0
            
            exists = unit_exists or e2e_exists
            if exists: documented += 1
            else: missing += 1
            
            # Drift (Max of unit/e2e vs code)
            # If doc is NEWER, drift is 0. If OLDER, drift is (Code - Doc).
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
