"""
HTML exporter for converting Markdown to styled HTML.

Generates pandoc-friendly HTML for optimal DOCX conversion.
Uses markdown2 with support for tables, code blocks, and semantic structure.
"""

import markdown2
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger("nibandha.export")


class HTMLExporter:
    """Converts Markdown to professionally styled, DOCX-friendly HTML."""
    
    def __init__(self, style_dir: Path = None):
        """
        Initialize HTML exporter.
        
        Args:
            style_dir: Directory containing CSS style files
                      Defaults to package styles directory
        """
        if style_dir is None:
            style_dir = Path(__file__).parent / "styles"
        self.style_dir = style_dir
    
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
        
        # Post-process for DOCX compatibility
        if docx_friendly:
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
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="generator" content="Nibandha Report System">
    <title>{title}</title>
    <style>
{css}
    </style>
</head>
<body>
    <article class="document">
{body}
    </article>
</body>
</html>"""
    
    def _get_inline_default_css(self) -> str:
        """
        Fallback inline CSS if no style files found.
        Uses only pandoc-compatible CSS properties.
        """
        return """
        body {
            font-family: 'Calibri', 'Arial', sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            color: #000000;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #1a1a1a;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }
        
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 1rem 0;
        }
        
        th, td {
            border: 1px solid #000000;
            padding: 8px 12px;
            text-align: left;
        }
        
        th {
            background-color: #f0f0f0;
            font-weight: bold;
        }
        
        code {
            background-color: #f5f5f5;
            padding: 2px 4px;
            font-family: 'Consolas', 'Courier New', monospace;
        }
        
        pre {
            background-color: #f5f5f5;
            padding: 1rem;
            overflow-x: auto;
            border: 1px solid #cccccc;
        }
        
        img {
            max-width: 100%;
            height: auto;
        }
        """

