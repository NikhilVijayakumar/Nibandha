import logging
import shutil
from pathlib import Path
from typing import Optional, List

from ...domain.protocols.exporter import ExporterProtocol

logger = logging.getLogger("nibandha.export.docx")

class DOCXExporter(ExporterProtocol):
    """
    Exports content to DOCX format using Pandoc (via pypandoc).
    Requires 'pypandoc' library and 'pandoc' executable installed.
    """
    
    def __init__(self):
        self._check_dependencies()
        
    def _check_dependencies(self):
        """Check if pypandoc and pandoc are available."""
        self.pypandoc_available = False
        try:
            import pypandoc
            self.pypandoc = pypandoc
            # Check for pandoc executable
            # pypandoc.get_pandoc_version() raises OSError if not found
            try:
                version = pypandoc.get_pandoc_version()
                logger.debug(f"Pandoc version: {version}")
                self.pypandoc_available = True
            except OSError:
                logger.warning("Pandoc executable not found. DOCX export will fail.")
                logger.warning("Please install pandoc: https://pandoc.org/installing.html")
        except ImportError:
            logger.warning("pypandoc library not installed. DOCX export disabled.")
            logger.warning("Install with: pip install pypandoc")

    def export(self, content_path: Path, output_path: Path, style: str = "default") -> Optional[Path]:
        """
        Convert an HTML file to DOCX.
        
        Args:
            content_path: Path to the source HTML file
            output_path: Path to write the DOCX file (without extension, or with)
            style: Style identifier (used to finding reference doc)
            
        Returns:
            Path to the generated file, or None if failed
        """
        if not self.pypandoc_available:
            logger.error("Cannot export to DOCX: Missing pandoc or pypandoc.")
            return None
            
        if not content_path.exists():
            logger.error(f"Source file not found: {content_path}")
            return None
            
        # Ensure output has .docx extension
        if output_path.suffix != ".docx":
            output_path = output_path.with_suffix(".docx")
            
        logger.info(f"Exporting DOCX to {output_path}...")
        
        # Determine extra arguments
        # We can use a reference docx if available in styles dir
        extra_args = [
            "--toc", # Table of Contents
            "--standalone",
        ]
        
        # Look for reference.docx in ../styles/
        # Assumes content_path or self location...
        # Let's assume styles dir relative to this file
        current_dir = Path(__file__).parent
        styles_dir = current_dir / "styles"
        ref_doc = styles_dir / "reference.docx"
        
        if ref_doc.exists():
            extra_args.append(f"--reference-doc={ref_doc}")
            logger.debug(f"Using reference doc: {ref_doc}")
            
        try:
            # Pypandoc convert_file
            # Format is 'html' to 'docx'
            output = self.pypandoc.convert_file(
                source_file=str(content_path),
                to='docx',
                outputfile=str(output_path),
                extra_args=extra_args
            )
            logger.info(f"Successfully exported DOCX: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to export DOCX: {e}")
            return None
