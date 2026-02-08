"""
Modern tab-based HTML exporter for unified reports.
Creates interactive dashboard-style HTML with navigation tabs.
"""
from pathlib import Path
from typing import List, Dict, Optional, Any
import markdown2
import logging
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger("nibandha.export.tabs")


from nibandha.export.infrastructure.base_exporter import BaseHTMLExporter

class TabBasedHTMLExporter(BaseHTMLExporter):
    """Exports markdown to interactive HTML with tab navigation."""
    
    def __init__(self, template_dir: Optional[Path] = None):
        super().__init__("nibandha.export.tabs")
        
        if template_dir is None:
            template_dir = Path(__file__).parent / "templates" / "tabs"
        self.template_dir = template_dir
        
        # Setup Jinja2 environment
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))
    
    def _build_html_document(
        self, 
        sections: List[Dict[str, Any]], 
        project_info: Dict[str, str]
    ) -> str:
        """Build complete HTML document with tabs."""
        
        # Load template
        template = self.jinja_env.get_template('document.html')
        
        # Load CSS and JavaScript
        css = self._get_css()
        javascript = self._get_javascript()
        
        # Render template
        return template.render(
            sections=sections,
            project_name=project_info.get('name', 'Quality Report'),
            status=project_info.get('status', ''),
            grade=project_info.get('grade', 'N/A'),
            css=css,
            javascript=javascript
        )
    
    def _get_css(self) -> str:
        """Modern dashboard CSS."""
        css_file = self.template_dir / "styles.css"
        if css_file.exists():
            return css_file.read_text(encoding='utf-8')
        
        logger.error("Tab dashboard CSS template not found")
        return ""
    
    def _get_javascript(self) -> str:
        """Tab switching JavaScript."""
        js_file = self.template_dir / "scripts.js"
        if js_file.exists():
            return js_file.read_text(encoding='utf-8')
        
        logger.error("Tab dashboard JavaScript template not found")
        return ""
