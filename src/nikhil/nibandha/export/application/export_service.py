import logging
from pathlib import Path
from typing import List, Optional

from ..domain.protocols.exporter import ExportFormat
from ..infrastructure.html_exporter import HTMLExporter
from ..infrastructure.docx_exporter import DOCXExporter
from ..infrastructure.modern_dashboard_exporter import ModernDashboardExporter

logger = logging.getLogger("nibandha.export")

class ExportService:
    """
    Orchestrates report export to multiple formats (HTML, DOCX).
    Handles dependencies between formats (e.g., DOCX requires HTML).
    """

    def __init__(self) -> None:
        self.html_exporter = HTMLExporter()
        self.docx_exporter = DOCXExporter()
        self.dashboard_exporter = ModernDashboardExporter()

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

    def export_unified_report(
        self,
        summary_path: Path,
        detail_paths: List[Path],
        output_dir: Path,
        formats: List[str],
        project_info: Optional[dict] = None
    ) -> List[Path]:
        """
        Export unified report combining summary and details into single HTML/DOCX.
        
        Args:
            summary_path: Path to summary.md
            detail_paths: List of paths to detail reports  
            output_dir: Directory where to save unified reports
            formats: List of formats to export ("html", "docx")
            project_info: Dict with project metadata (name, grade, status)
            
        Returns:
            List of paths to generated unified files
        """
        logger.info(f"Exporting unified report with {len(detail_paths) + 1} sections")
        
        generated_files = []
        
        # Read and prepare sections
        sections: List[dict] = []
        
        # Add summary
        if summary_path.exists():
            content = summary_path.read_text(encoding="utf-8")
            content = self._remove_frontmatter(content)
            sections.append({"title": "Summary", "content": content, "metrics_cards": []})
        
        # Add details with metrics cards extraction from JSON
        for detail_path in detail_paths:
            if detail_path.exists():
                content = detail_path.read_text(encoding="utf-8")
                content = self._remove_frontmatter(content)
                title = detail_path.stem.replace('_', ' ').title()
                
                # Try to load metrics cards from corresponding JSON
                metrics_cards = self._load_metrics_cards(detail_path)
                
                sections.append({"title": title, "content": content, "metrics_cards": metrics_cards})
        
        # Export to HTML with modern dashboard
        if "html" in formats and sections:
            html_path = output_dir / "complete_report.html"
            try:
                self.dashboard_exporter.export(sections, html_path, project_info)
                generated_files.append(html_path)
                logger.info(f"Modern dashboard HTML exported: {html_path}")
            except Exception as e:
                logger.error(f"Failed to export modern dashboard HTML: {e}")
        
        
        # Export to DOCX
        if "docx" in formats and sections:
            # Create temporary unified markdown
            temp_md = output_dir / "temp_unified.md"
            unified_content = self._build_unified_markdown(sections, project_info)
            temp_md.write_text(unified_content, encoding="utf-8")
            
            try:
                # Convert to HTML first (for pandoc)
                temp_html = temp_md.with_suffix(".html")
                self.html_exporter.export(
                    unified_content,
                    temp_html,
                    style="default",
                    docx_friendly=True
                )
                
                # Convert HTML to DOCX
                docx_path = output_dir / "complete_report.docx"
                self.docx_exporter.export(temp_html, docx_path, style="default")
                
                # Cleanup temp files
                if temp_md.exists():
                    temp_md.unlink()
                if temp_html.exists():
                    temp_html.unlink()
                
                generated_files.append(docx_path)
                logger.info(f"Unified DOCX exported: {docx_path}")
            except Exception as e:
                logger.error(f"Failed to export unified DOCX: {e}")
        
        return generated_files
    
    def _remove_frontmatter(self, content: str) -> str:
        """Remove YAML frontmatter from markdown."""
        lines = content.split('\n')
        if lines and lines[0].strip() == '---':
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    return '\n'.join(lines[i+1:])
        return content
    
    def _load_metrics_cards(self, detail_path: Path) -> List[dict]:
        """Load metrics cards from corresponding JSON file."""
        # Construct JSON path from detail markdown path
        # detail_path like: output_dir/details/unit_report.md
        # JSON would be: output_dir/assets/data/unit.json
        
        json_name_map = {
            "unit_report": "unit",
            "e2e_report": "e2e",
            "type_safety_report": "type_safety",
            "complexity_report": "complexity"
        }
        
        detail_stem = detail_path.stem
        json_name = json_name_map.get(detail_stem)
        
        if not json_name:
            return []
        
        json_path = detail_path.parent.parent / "assets" / "data" / f"{json_name}.json"
        
        if not json_path.exists():
            return []
        
        try:
            import json
            import json
            with open(json_path, 'r') as f:
                data = json.load(f)
                result: List[dict] = data.get("metrics_cards", [])
                return result
        except Exception as e:
            logger.warning(f"Failed to load metrics cards from {json_path}: {e}")
            return []
    
    def _build_unified_markdown(self, sections: List[dict], project_info: Optional[dict] = None) -> str:
        """Build unified markdown with proper frontmatter."""
        from datetime import datetime
        
        if not project_info:
            project_info = {}
        
        frontmatter = f"""---
title: "Nibandha Quality Report"
subtitle: "Complete Project Analysis"
author: "Generated by Nibandha"
date: "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
toc: true
lof: true
lot: true
---

"""
        
        content = frontmatter
        for section in sections:
            content += f"\n\n---\n\n{section['content']}\n"
        
        return content
