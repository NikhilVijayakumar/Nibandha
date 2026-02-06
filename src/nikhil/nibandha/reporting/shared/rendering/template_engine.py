from pathlib import Path
from typing import Dict, Any, Optional
import json

class TemplateEngine:
    """Renders markdown templates using JSON data."""
    
    def __init__(self, templates_dir: Path, defaults_dir: Optional[Path] = None):
        """
        Args:
            templates_dir: Path to directory containing .md template files
            defaults_dir: Fallback directory if template not found in templates_dir
        """
        self.templates_dir = templates_dir
        self.defaults_dir = defaults_dir
    
    def render(
        self, 
        template_name: str, 
        data: Dict[str, Any],
        output_path: Optional[Path] = None
    ) -> str:
        """
        Render a template with provided data using Jinja2.
        
        Args:
            template_name: Name of template file (e.g., "unit_report_template.md")
            data: Dictionary of key-value pairs to substitute in template
            output_path: Optional path to save rendered markdown
            
        Returns:
            Rendered markdown content
            
        Raises:
            TemplateNotFound: If template file does not exist
        """
        from jinja2 import Environment, FileSystemLoader, select_autoescape, StrictUndefined
        
        # Setup loader with fallback
        search_paths = [str(self.templates_dir)]
        if self.defaults_dir:
            search_paths.append(str(self.defaults_dir))
            
        env = Environment(
            loader=FileSystemLoader(search_paths),
            autoescape=select_autoescape(['html', 'xml']),
            undefined=StrictUndefined
        )
        
        template = env.get_template(template_name)
        content = template.render(**data)
        
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding="utf-8")
        
        return content
    
    def save_data(self, data: Dict[str, Any], data_path: Path) -> None:
        """
        Save report data as JSON for reference and debugging.
        
        Args:
            data: Dictionary of report data
            data_path: Path to save JSON file
        """
        data_path.parent.mkdir(parents=True, exist_ok=True)
        data_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
