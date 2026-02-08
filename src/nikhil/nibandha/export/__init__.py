"""
Export module for converting Markdown documents to HTML and DOCX formats.

This module provides reusable export functionality for:
- Reports (unit tests, quality, dependencies, etc.)
- Documentation (functional, technical, test scenarios)

Usage:
    from nibandha.configuration.domain.models.export_config import ExportConfig
    from nibandha.export import ExportService
    
    # Create configuration
    config = ExportConfig(
        formats=["html", "docx"],
        style="default",
        template_dir=Path("templates"),
        styles_dir=Path("styles"),
        output_dir=Path("output"),
        output_filename="report"
    )
    
    # Create service with config
    service = ExportService(config)
    service.export_document(Path("report.md"))
"""

from nibandha.export.application.export_service import ExportService
from nibandha.export.domain.protocols.exporter import ExportFormat

__all__ = ["ExportService", "ExportFormat"]
