"""
Modern sidebar-based HTML dashboard exporter.
Replaces tab-based layout with sidebar + card-based metrics dashboard.
"""
from pathlib import Path
from typing import List, Dict, Optional, Any
import markdown2
import logging
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger("nibandha.export.dashboard")


from nibandha.export.infrastructure.base_exporter import BaseHTMLExporter

class ModernDashboardExporter(BaseHTMLExporter):
    """Exports markdown to modern sidebar-based dashboard HTML."""
    
    def __init__(self, template_dir: Optional[Path] = None):
        super().__init__("nibandha.export.dashboard")
        
        if template_dir is None:
            template_dir = Path(__file__).parent / "templates" / "dashboard"
        self.template_dir = template_dir
        
        # Setup Jinja2 environment
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))
    
    def _build_html_document(
        self, 
        sections: List[Dict[str, Any]], 
        project_info: Dict[str, str]
    ) -> str:
        """Build complete HTML document with sidebar and cards."""
        
        # Add icons to sections
        for section in sections:
            if 'icon' not in section:
                section['icon'] = self._get_section_icon(section['title'])
        
        # Load template
        template = self.jinja_env.get_template('document.html')
        
        # Load CSS and JavaScript
        css = self._get_css()
        javascript = self._get_javascript()
        
        # Render template
        return template.render(
            sections=sections,
            project_name=project_info.get('name', 'Quality Dashboard'),
            status=project_info.get('status', 'In Progress'),
            grade=project_info.get('grade', 'N/A'),
            css=css,
            javascript=javascript
        )
    
    def _get_section_icon(self, title: str) -> str:
        """Get icon for section based on title."""
        icons = {
            "summary": "📊",
            "unit": "🧪",
            "e2e": "🔗",
            "type": "🔒",
            "complexity": "📈",
            "architecture": "🏗️",
            "documentation": "📚",
            "module": "📦",
            "package": "📦"
        }
        
        title_lower = title.lower()
        for key, icon in icons.items():
            if key in title_lower:
                return icon
        return "📄"
    
    def _get_css(self) -> str:
        """Modern dashboard CSS with sidebar layout."""
        css_file = self.template_dir / "styles.css"
        if css_file.exists():
            return css_file.read_text(encoding='utf-8')
        
        logger.error("Modern dashboard CSS template not found")
        return ""
    
    def _get_javascript(self) -> str:
        """JavaScript for theme toggle and smooth scrolling."""
        js_file = self.template_dir / "scripts.js"
        if js_file.exists():
            return js_file.read_text(encoding='utf-8')
        
        logger.error("Modern dashboard JavaScript template not found")
        return ""
