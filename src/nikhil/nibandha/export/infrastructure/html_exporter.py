"""
HTML exporter for converting Markdown to styled HTML.

Generates pandoc-friendly HTML for optimal DOCX conversion.
Uses markdown2 with support for tables, code blocks, and semantic structure.
"""

import markdown2
from pathlib import Path
from typing import Optional
import logging
from jinja2 import Environment, FileSystemLoader

from nibandha.export.application.helpers.mermaid_processor import MermaidProcessor
from nibandha.export.application.helpers.math_processor import MathProcessor

logger = logging.getLogger("nibandha.export")


class HTMLExporter:
    """Converts Markdown to professionally styled, DOCX-friendly HTML."""
    
    def __init__(self, style_dir: Optional[Path] = None, template_dir: Optional[Path] = None):
        """
        Initialize HTML exporter.
        
        Args:
            style_dir: Directory containing CSS style files
                      Defaults to package styles directory
            template_dir: Directory containing HTML templates
                         Defaults to package templates/html directory
        """
        if style_dir is None:
            style_dir = Path(__file__).parent / "styles"
        self.style_dir = style_dir
        
        if template_dir is None:
            template_dir = Path(__file__).parent / "templates" / "html"
        self.template_dir = template_dir
        
        # Setup Jinja2 environment
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))
    
    def export(
        self,
        content: str,
        output_path: Path,
        style: str = "default",
        docx_friendly: bool = True
    ) -> Path:
        """
        Export markdown to HTML with styling.
        
        Args:
            content: Markdown content to convert
            output_path: Output file path (without extension)
            style: Style/theme name (default, professional, documentation)
            docx_friendly: If True, generates HTML optimized for DOCX conversion
            
        Returns:
            Path to generated HTML file
        """
        logger.info(f"Exporting HTML: {output_path.name} with style '{style}'")
        
        # Pre-process math and mermaid blocks
        content, math_store = MathProcessor.pre_process(content)
        content, mermaid_store = MermaidProcessor.pre_process(content)
        
        # Convert MD to HTML with semantic structure
        html_body = markdown2.markdown(
            content,
            extras=[
                "tables",
                "fenced-code-blocks", 
                "code-friendly",
                "header-ids",
                "metadata",
                "break-on-newline",
                "cuddled-lists",  # Better list formatting
                "toc"
            ]
        )
        
        # Restore mermaid and math blocks
        html_body = MermaidProcessor.post_process(html_body, mermaid_store)
        html_body = MathProcessor.post_process(html_body, math_store)
        
        # Post-process for DOCX compatibility
        if docx_friendly:
            html_body = MermaidProcessor.convert_to_image_tags(html_body)
            html_body = self._make_docx_friendly(html_body)
        
        # Load CSS style
        css = self._load_style(style)
        
        # Create complete HTML document
        title = output_path.stem.replace('_', ' ').title()
        html = self._create_html_document(html_body, css, title)
        
        # Write to file
        output_file = output_path.with_suffix('.html')
        output_file.write_text(html, encoding='utf-8')
        
        logger.info(f"HTML exported successfully: {output_file}")
        return output_file
    
    def _make_docx_friendly(self, html: str) -> str:
        """
        Post-process HTML for better DOCX conversion.
        
        Ensures:
        - Clean semantic structure
        - Proper heading hierarchy
        - Standard table formatting
        """
        # Replace any problematic elements
        # Pandoc handles standard HTML well, so mostly just cleanup
        
        # Ensure proper paragraph spacing
        html = html.replace('<p><br /></p>', '<p>&nbsp;</p>')
        
        # Clean up extra whitespace that might confuse pandoc
        import re
        html = re.sub(r'\n\s*\n\s*\n', '\n\n', html)
        
        return html
    
    def _load_style(self, style: str) -> str:
        """Load CSS style from file."""
        style_file = self.style_dir / f"{style}.css"
        
        if not style_file.exists():
            logger.warning(f"Style '{style}' not found, using default")
            style_file = self.style_dir / "default.css"
        
        if not style_file.exists():
            logger.warning("No CSS files found, using inline default")
            return self._get_inline_default_css()
        
        return style_file.read_text(encoding='utf-8')
    
    def _create_html_document(self, body: str, css: str, title: str) -> str:
        """
        Create complete HTML document with pandoc-compatible structure.
        
        Uses semantic HTML5 elements and clean structure for optimal
        DOCX conversion via pandoc.
        """
        template = self.jinja_env.get_template('document.html')
        style_tag = f"<style>\n{css}\n</style>"
        return template.render(title=title, style_tag=style_tag, body=body)
    
    def _get_inline_default_css(self) -> str:
        """
        Fallback inline CSS if no style files found.
        Uses only pandoc-compatible CSS properties.
        """
        fallback_css = self.template_dir / "styles" / "fallback.css"
        if fallback_css.exists():
            return fallback_css.read_text(encoding='utf-8')
        
        # Ultimate fallback if even the template file is missing
        logger.error("Fallback CSS template not found, using minimal inline CSS")
        return "body { font-family: Arial, sans-serif; padding: 2rem; }"

