import logging
from pathlib import Path
from typing import List, Optional

from ...domain.protocols.exporter import ExportFormat
from ...infrastructure.html_exporter import HTMLExporter
from ...infrastructure.docx_exporter import DOCXExporter

logger = logging.getLogger("nibandha.export")

class ExportService:
    """
    Orchestrates report export to multiple formats (HTML, DOCX).
    Handles dependencies between formats (e.g., DOCX requires HTML).
    """

    def __init__(self):
        self.html_exporter = HTMLExporter()
        self.docx_exporter = DOCXExporter()

    def export_document(
        self,
        markdown_path: Path,
        formats: List[str],  # "html", "docx"
        style: str = "default"
    ) -> List[Path]:
        """
        Export a markdown document to specified formats.
        
        Args:
            markdown_path: Path to source markdown file
            formats: List of target formats ("html", "docx")
            style: Style name for HTML/DOCX
            
        Returns:
            List of paths to generated files
        """
        if not markdown_path.exists():
            logger.error(f"Markdown file not found: {markdown_path}")
            return []

        generated_files = []
        content = markdown_path.read_text(encoding="utf-8")
        
        # Determine strict dependencies
        # DOCX requires HTML generation first
        needs_html = "html" in formats or "docx" in formats
        
        html_path = None
        
        if needs_html:
            # Output path logic: same directory and name as markdown
            # e.g. report.md -> report.html
            target_html_path = markdown_path.with_suffix(".html")
            
            # DOCX conversion works best with "docx_friendly" HTML
            # If the user specifically asked for HTML, they get the friendly version too.
            # This is generally fine as it just avoids some complex CSS that pandoc hates.
            docx_friendly = "docx" in formats
            
            html_path = self.html_exporter.export(
                content, 
                target_html_path, 
                style=style,
                docx_friendly=docx_friendly
            )
            
            if html_path:
                if "html" in formats:
                    generated_files.append(html_path)
            else:
                 logger.error("HTML export failed, aborting dependent exports.")
                 return generated_files

        if "docx" in formats:
            if html_path and html_path.exists():
                target_docx_path = markdown_path.with_suffix(".docx")
                docx_path = self.docx_exporter.export(
                    html_path,
                    target_docx_path,
                    style=style
                )
                if docx_path:
                    generated_files.append(docx_path)
            else:
                logger.error("Cannot export DOCX: Intermediate HTML missing.")

        # Cleanup if HTML wasn't requested but was generated for DOCX
        if "html" not in formats and "docx" in formats and html_path:
            try:
                # Optional: Delete intermediate HTML?
                # Usually users might want to debug, but for cleanness we could delete.
                # Let's keep it for now or make it a hidden temp file. 
                # Keeping it is safer for debugging.
                # Or renaming it to .tmp.
                pass
            except Exception as e:
                logger.warning(f"Failed to cleanup temp HTML: {e}")

        return generated_files
