import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from nibandha.configuration.domain.models.export_config import ExportConfig
from nibandha.export.domain.protocols.exporter import ExportFormat
from nibandha.export.infrastructure.html_exporter import HTMLExporter
from nibandha.export.infrastructure.docx_exporter import DOCXExporter
from nibandha.export.infrastructure.modern_dashboard_exporter import ModernDashboardExporter
from nibandha.export.application.helpers import (
    MarkdownProcessor,
    MetricsCardLoader,
    UnifiedReportBuilder
)

logger = logging.getLogger("nibandha.export")

class ExportService:
    """
    Orchestrates report export to multiple formats (HTML, DOCX).
    
    Responsibilities:
    - Validate configuration
    - Coordinate exporter infrastructure
    - Delegate processing to helper classes
    """

    def __init__(
        self, 
        config: ExportConfig,
        markdown_processor: Optional[MarkdownProcessor] = None,
        metrics_loader: Optional[MetricsCardLoader] = None
    ) -> None:
        """
        Initialize ExportService with dependencies.
        
        Args:
            config: ExportConfig with all necessary paths and settings
            markdown_processor: Optional custom markdown processor
            metrics_loader: Optional custom metrics loader
            
        Raises:
            ValueError: If critical configuration is missing or invalid
        """
        self._validate_config(config)
        self.config = config
        
        # Initialize exporters with configuration paths (or None for defaults)
        # Strategy: Try to use the configured path. If it doesn't exist, fall back to internal default.
        # This handles the case where "src/nikhil/..." is in config but user is running as installed package.
        
        template_html = None
        template_dash = None
        
        if config.template_dir:
            # Check if explicit path exists
            if config.template_dir.exists():
                template_html = config.template_dir / "html"
                template_dash = config.template_dir / "dashboard"
            else:
                 # It might be a relative path that doesn't exist in CWD (e.g. installed package)
                 # We log a warning but let the exporter handle the fallback (by passing None)
                 # Wait, Exporter handles None by using internal path.
                 # So if config.template_dir is set but invalid, we passing None is the right fallback.
                 logger.debug(f"Configured template_dir {config.template_dir} not found, using internal defaults")
                 template_html = None
                 template_dash = None
        
        # Styles
        style_dir = None
        if config.styles_dir:
            if config.styles_dir.exists():
                style_dir = config.styles_dir
            else:
                logger.debug(f"Configured styles_dir {config.styles_dir} not found, using internal defaults")
                style_dir = None

        self.html_exporter = HTMLExporter(
            template_dir=template_html,
            style_dir=style_dir
        )
        self.docx_exporter = DOCXExporter()
        self.dashboard_exporter = ModernDashboardExporter(
            template_dir=template_dash
        )
        
        self.markdown_processor = markdown_processor or MarkdownProcessor()
        self.metrics_loader = metrics_loader
        
        logger.info(f"ExportService initialized with formats: {config.formats}, style: {config.style}")

    def _validate_config(self, config: ExportConfig) -> None:
        """
        Validate critical configuration.
        
        Args:
            config: Configuration to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Template and Styles dirs are optional (internal defaults used if None or invalid)
        # We don't raise error if they don't exist, we just log warning and fallback (handled in __init__)
        if config.template_dir and not config.template_dir.exists():
             logger.warning(f"Template directory not found: {config.template_dir}. Will try to use internal defaults.")
        
        if config.styles_dir and not config.styles_dir.exists():
             logger.warning(f"Styles directory not found: {config.styles_dir}. Will try to use internal defaults.")
        
        if not config.output_dir:
            logger.error("Export configuration missing output_dir")
            raise ValueError("Invalid export configuration: output_dir is required")
        
        # Ensure output directory exists
        config.output_dir.mkdir(parents=True, exist_ok=True)

    def export_document(self, markdown_path: Path) -> List[Path]:
        """
        Export a markdown document to configured formats.
        
        Args:
            markdown_path: Path to source markdown file
            
        Returns:
            List of paths to generated files
        """
        if not markdown_path.exists():
            logger.error(f"Markdown file not found: {markdown_path}")
            return []

        generated_files = []
        content = markdown_path.read_text(encoding="utf-8")
        
        # Use configuration
        formats = self.config.formats
        style = self.config.style
        
        # Determine dependencies (DOCX requires HTML)
        needs_html = "html" in formats or "docx" in formats
        
        html_path = None
        
        if needs_html:
            # Generate HTML
            output_filename = self.config.output_filename or markdown_path.stem
            target_html_path = self.config.output_dir / f"{output_filename}.html"
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
                output_filename = self.config.output_filename or markdown_path.stem
                target_docx_path = self.config.output_dir / f"{output_filename}.docx"
                docx_path = self.docx_exporter.export(
                    html_path,
                    target_docx_path,
                    style=style
                )
                if docx_path:
                    generated_files.append(docx_path)
            else:
                logger.error("Cannot export DOCX: Intermediate HTML missing.")

        return generated_files

    def export_batch(self) -> Dict[str, List[Path]]:
        """
        Export all markdown files from configured input_dir.
        
        Uses FileDiscovery to find files, apply exclusions, and order them.
        Each file is exported to all configured formats with consistent ordering.
        
        Returns:
            Dictionary mapping source file stem to list of generated export paths
            
        Raises:
            ValueError: If input_dir is not configured
        """
        from nibandha.export.application.helpers import FileDiscovery
        
        # Discover files using config
        discovery = FileDiscovery(self.config)
        markdown_files = discovery.discover_files()
        
        if not markdown_files:
            logger.warning("No files to export")
            return {}
        
        logger.info(f"Batch exporting {len(markdown_files)} markdown files")
        
        results: Dict[str, List[Path]] = {}
        
        for markdown_file in markdown_files:
            logger.info(f"Exporting: {markdown_file.name}")
            
            # Set output filename for this specific file
            original_filename = self.config.output_filename
            self.config.output_filename = markdown_file.stem
            
            try:
                exported_files = self.export_document(markdown_file)
                results[markdown_file.stem] = exported_files
            except Exception as e:
                logger.error(f"Failed to export {markdown_file.name}: {e}")
                results[markdown_file.stem] = []
            finally:
                # Restore original filename
                self.config.output_filename = original_filename
        
        logger.info(f"Batch export complete: {len(results)} files processed")
        return results

    def export_combined(self) -> List[Path]:
        """
        Export all markdown files combined into a single document.
        
        Uses FileDiscovery to find and order files, then concatenates them
        before exporting to configured formats.
        
        Returns:
            List of generated file paths
        """
        from nibandha.export.application.helpers import FileDiscovery
        
        # Discover files using config
        discovery = FileDiscovery(self.config)
        markdown_files = discovery.discover_files()
        
        if not markdown_files:
            logger.warning("No files to export combined")
            return []
            
        logger.info(f"Combining {len(markdown_files)} markdown files for export")
        
        # Build sections structure to reuse unified export logic
        from nibandha.export.application.helpers.unified_report_builder import UnifiedReportSection
        
        sections = []
        for file_path in markdown_files:
            content = file_path.read_text(encoding="utf-8")
            # Strip frontmatter
            content = self.markdown_processor.remove_frontmatter(content)
            title = file_path.stem.replace('_', ' ').title()
            
            # Load metrics cards if configured mapping matches
            metrics_cards = []
            if self.metrics_loader:
                try:
                    metrics_cards = self.metrics_loader.load_cards(file_path)
                except Exception as e:
                    logger.debug(f"Could not load metrics cards for {file_path.name}: {e}")
            
            sections.append(UnifiedReportSection(
                title=title,
                content=content,
                metrics_cards=metrics_cards
            ))
            
        return self._export_sections(sections, project_info=None)

    def export_unified_report(
        self,
        summary_path: Path,
        detail_paths: List[Path],
        project_info: Optional[Dict[str, Any]] = None,
        metrics_loader: Optional[MetricsCardLoader] = None
    ) -> List[Path]:
        """
        Export unified report combining summary and details.
        
        Args:
            summary_path: Path to summary markdown file
            detail_paths: List of paths to detail report markdown files
            project_info: Optional project metadata
            metrics_loader: Optional custom metrics loader (overrides instance loader)
            
        Returns:
            List of paths to generated unified files
        """
        logger.info(f"Exporting unified report with {len(detail_paths) + 1} sections")
        
        # Use provided loader or instance loader
        loader = metrics_loader or self.metrics_loader
        if not loader:
            logger.warning("No metrics loader provided, metrics cards will be empty")
        
        # Build sections using helper
        builder = UnifiedReportBuilder(self.markdown_processor, loader)
        sections = builder.build_sections(summary_path, detail_paths)
        
        # Export sections to configured formats
        return self._export_sections(sections, project_info)
    
    def _export_sections(
        self,
        sections: List[Any],  # List[UnifiedReportSection]
        project_info: Optional[Dict[str, Any]]
    ) -> List[Path]:
        """
        Export sections to configured formats.
        
        Args:
            sections: List of report sections
            project_info: Optional project metadata
            
        Returns:
            List of generated file paths
        """
        generated_files = []
        formats = self.config.formats
        output_dir = self.config.output_dir
        output_filename = self.config.output_filename
        
        # Convert sections to dicts for exporters
        section_dicts = [
            {"title": s.title, "content": s.content, "metrics_cards": s.metrics_cards}
            for s in sections
        ]
        
        # Export to HTML with modern dashboard
        if "html" in formats and section_dicts:
            html_path = output_dir / f"{output_filename}.html"
            try:
                self.dashboard_exporter.export(section_dicts, html_path, project_info)
                generated_files.append(html_path)
                logger.info(f"Modern dashboard HTML exported: {html_path}")
            except Exception as e:
                logger.error(f"Failed to export modern dashboard HTML: {e}")
        
        # Export to DOCX
        if "docx" in formats and section_dicts:
            temp_md = output_dir / "temp_unified.md"
            unified_content = self.markdown_processor.build_unified_markdown(section_dicts, project_info)
            temp_md.write_text(unified_content, encoding="utf-8")
            
            try:
                # Convert to HTML first (for pandoc)
                temp_html = temp_md.with_suffix(".html")
                self.html_exporter.export(
                    unified_content,
                    temp_html,
                    style=self.config.style,
                    docx_friendly=True
                )
                
                # Convert HTML to DOCX
                docx_path = output_dir / f"{output_filename}.docx"
                self.docx_exporter.export(temp_html, docx_path, style=self.config.style)
                
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
