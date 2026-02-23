from pathlib import Path
from typing import List, Dict, Optional, Any
import markdown2
import logging
import re
from abc import ABC, abstractmethod

from nibandha.export.application.helpers.mermaid_processor import MermaidProcessor
from nibandha.export.application.helpers.math_processor import MathProcessor

class BaseHTMLExporter(ABC):
    """Base class for HTML exporters to prevent duplication."""
    
    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)

    def export(
        self,
        markdown_sections: List[Dict[str, Any]],
        output_path: Path,
        project_info: Optional[Dict[str, str]] = None
    ) -> Path:
        """
        Export markdown sections to HTML.
        
        Args:
            markdown_sections: List of sections with 'title', 'content', etc.
            output_path: Destination path
            project_info: Optional project metadata
            
        Returns:
            Path to saved file
        """
        self.logger.info(f"Exporting HTML with {len(markdown_sections)} sections")
        
        if not project_info:
            project_info = {
                "name": "Quality Report",
                "grade": "N/A",
                "status": "Complete"
            }
        
        # Convert markdown sections to HTML
        html_sections = []
        for section in markdown_sections:
            content, math_store = MathProcessor.pre_process(section["content"])
            content, mermaid_store = MermaidProcessor.pre_process(content)
            
            html_content = markdown2.markdown(
                content,
                extras=[
                    "tables",
                    "fenced-code-blocks",
                    "header-ids",
                    "break-on-newline",
                    "metadata"
                ]
            )
            
            
            html_content = MermaidProcessor.post_process(html_content, mermaid_store)
            html_content = MathProcessor.post_process(html_content, math_store)
            
            # Unified ID generation: strip leading numbers, slugify
            clean_title = re.sub(r'^\d+[\s_-]*', '', section["title"])
            section_id = clean_title.lower().replace(" ", "-")
            
            html_sections.append({
                "title": section["title"],
                "id": section_id,
                "content": html_content,
                "metrics_cards": section.get("metrics_cards", [])
            })
        
        # Build complete HTML document
        html = self._build_html_document(html_sections, project_info)
        
        # Write output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")
        
        self.logger.info(f"HTML saved to: {output_path}")
        return output_path

    @abstractmethod
    def _build_html_document(
        self, 
        sections: List[Dict[str, Any]], 
        project_info: Dict[str, str]
    ) -> str:
        """Build the specific HTML structure."""
        pass
    
    @abstractmethod
    def _get_css(self) -> str:
        """Get CSS styles."""
        pass

    @abstractmethod
    def _get_javascript(self) -> str:
        """Get JavaScript."""
        pass
