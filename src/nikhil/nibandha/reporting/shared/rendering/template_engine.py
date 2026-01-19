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
        Render a template with provided data.
        
        Args:
            template_name: Name of template file (e.g., "unit_report_template.md")
            data: Dictionary of key-value pairs to substitute in template
            output_path: Optional path to save rendered markdown
            
        Returns:
            Rendered markdown content
            
        Raises:
            FileNotFoundError: If template file does not exist
            ValueError: If data is missing keys required by the template
        """
        template_path = self.templates_dir / template_name
        
        if not template_path.exists():
            if self.defaults_dir:
                fallback_path = self.defaults_dir / template_name
                if fallback_path.exists():
                    template_path = fallback_path
            
            if not template_path.exists():
                raise FileNotFoundError(f"Template not found: {template_path} (checked {self.templates_dir} and {self.defaults_dir})")
        
        template = template_path.read_text(encoding="utf-8")
        
        # Use format with safe error handling
        try:
            content = template.format(**data)
        except KeyError as e:
            missing_key = e.args[0]
            raise ValueError(
                f"Template '{template_name}' requires key '{missing_key}' "
                f"which was not provided in data"
            )
        
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding="utf-8")
        
        return content
    
    def save_data(self, data: Dict[str, Any], data_path: Path):
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
