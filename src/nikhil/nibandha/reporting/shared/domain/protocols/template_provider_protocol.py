from typing import Protocol, Dict, Any, Optional
from pathlib import Path

class TemplateProviderProtocol(Protocol):
    """Protocol for template rendering operations."""
    
    def render(
        self, 
        template_name: str, 
        data: Dict[str, Any],
        output_path: Optional[Path] = None
    ) -> str:
        """
        Render a template with provided data.
        
        Args:
            template_name: Name of the template file.
            data: Data to inject into the template.
            output_path: Optional path to save the rendered output.
            
        Returns:
            Rendered content as string.
        """
        ...
    
    def save_data(self, data: Dict[str, Any], data_path: Path) -> None:
        """
        Save raw data used for reporting.
        
        Args:
            data: Data to save.
            data_path: Location to save the data.
        """
        ...
