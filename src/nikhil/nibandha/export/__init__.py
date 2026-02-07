"""
Export module for converting Markdown documents to HTML and DOCX formats.

This module provides reusable export functionality for:
- Reports (unit tests, quality, dependencies, etc.)
- Documentation (functional, technical, test scenarios)

Usage:
except ImportError:
    # Optional export dependencies not present
    ExportService = None # type: ignore
    ExportFormat = None # type: ignore
else:
    from nibandha.export import ExportService, ExportFormat
    
    service = ExportService()
    service.export_document(
        Path("report.md"),
        formats=[ExportFormat.HTML, ExportFormat.DOCX]
    )
"""

from nibandha.export.application.export_service import ExportService
from nibandha.export.domain.protocols.exporter import ExportFormat

__all__ = ["ExportService", "ExportFormat"]
