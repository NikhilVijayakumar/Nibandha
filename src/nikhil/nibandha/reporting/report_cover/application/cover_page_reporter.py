import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import logging
import toml

from nibandha.reporting.shared.rendering.template_engine import TemplateEngine

logger = logging.getLogger("nibandha.reporting.report_cover")

class CoverPageReporter:
    def __init__(
        self, 
        output_dir: Path, 
        templates_dir: Path,
        template_engine: Optional[TemplateEngine] = None
    ):
        self.output_dir = output_dir
        self.templates_dir = templates_dir
        self.template_engine = template_engine or TemplateEngine(templates_dir)
        self.details_dir = output_dir / "details"
        self.details_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, project_root: Path, timestamp: str) -> Dict[str, Any]:
        """Generates the cover page."""
        logger.info("Generating Cover Page...")
        
        # 1. Read pyproject.toml
        project_name = "Nibandha Quality Report"
        project_version = "0.1.0"
        
        pyproject_path = project_root / "pyproject.toml"
        if pyproject_path.exists():
            try:
                data = toml.load(pyproject_path)
                project_name = data.get("project", {}).get("name", project_name)
                project_version = data.get("project", {}).get("version", project_version)
            except Exception as e:
                logger.warning(f"Failed to read pyproject.toml: {e}")
        
        # 2. Prepare Data
        mapping = {
            "project_name": project_name,
            "project_version": project_version,
            "timestamp": timestamp,
            "year": datetime.datetime.now().year
        }
        
        # 3. Render
        output_path = self.details_dir / "00_cover_page.md"
        self.template_engine.render("cover_page_template.md", mapping, output_path)
        
        return mapping
