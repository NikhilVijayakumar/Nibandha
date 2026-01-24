"""
Export protocol and format definitions.

Defines the contract for document export functionality.
"""

from typing import Protocol, Optional
from pathlib import Path
from enum import Enum


class ExportFormat(Enum):
    """Supported export formats."""
    
    MARKDOWN = "md"
    HTML = "html"
    DOCX = "docx"
    
    def __str__(self):
        return self.value


class ExporterProtocol(Protocol):
    """
    Protocol for document export.
    
    Implementations should convert markdown documents to various formats
    while preserving formatting, images, tables, and code blocks.
    
    Example:
        >>> class MyExporter:
        ...     def export(self, content: str, output_path: Path, 
        ...                format: ExportFormat, style: str = None) -> Path:
        ...         # Implementation here
        ...         pass
    """
    
    def export(
        self,
        content: str,
        output_path: Path,
        format: ExportFormat,
        style: Optional[str] = None
    ) -> Path:
        """
        Export markdown content to specified format.
        
        Args:
            content: Markdown content to export
            output_path: Output file path (without extension)
            format: Target export format
            style: Optional style/theme name (e.g., "default", "professional")
            
        Returns:
            Path to exported file
            
        Raises:
            ExportError: If export fails
        """
        ...
