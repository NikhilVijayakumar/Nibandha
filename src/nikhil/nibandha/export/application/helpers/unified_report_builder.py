"""Helper class for building unified reports from sections."""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from nibandha.export.application.helpers.markdown_processor import MarkdownProcessor
from nibandha.export.application.helpers.metrics_card_loader import MetricsCardLoader

logger = logging.getLogger("nibandha.export.helpers")


class UnifiedReportSection(BaseModel):
    """A section in the unified report."""
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Markdown content")
    metrics_cards: List[Dict[str, Any]] = Field(default_factory=list, description="Metrics cards for this section")
    
    class Config:
        frozen = True  # Immutable


class UnifiedReportBuilder:
    """
    Builds unified reports from markdown sections.
    
    Responsibilities:
    - Read and process markdown files
    - Load metrics cards for each section
    - Assemble sections into structured format
    """
    
    def __init__(
        self, 
        markdown_processor: MarkdownProcessor,
        metrics_loader: MetricsCardLoader | None = None
    ):
        """
        Initialize builder with dependencies.
        
        Args:
            markdown_processor: Processor for markdown operations
            metrics_loader: Optional loader for metrics cards
        """
        self.markdown_processor = markdown_processor
        self.metrics_loader = metrics_loader
    
    def build_sections(
        self,
        summary_path: Path,
        detail_paths: List[Path]
    ) -> List[UnifiedReportSection]:
        """
        Build sections from markdown files.
        
        Args:
            summary_path: Path to summary markdown file
            detail_paths: List of paths to detail report markdown files
            
        Returns:
            List of structured report sections
        """
        sections: List[UnifiedReportSection] = []
        
        # Add summary section
        if summary_path.exists():
            content = summary_path.read_text(encoding="utf-8")
            content = self.markdown_processor.remove_frontmatter(content)
            sections.append(UnifiedReportSection(
                title="Summary",
                content=content,
                metrics_cards=[]
            ))
        else:
            logger.warning(f"Summary file not found: {summary_path}")
        
        # Add detail sections
        for detail_path in detail_paths:
            if not detail_path.exists():
                logger.warning(f"Detail file not found: {detail_path}")
                continue
            
            content = detail_path.read_text(encoding="utf-8")
            content = self.markdown_processor.remove_frontmatter(content)
            title = detail_path.stem.replace('_', ' ').title()
            
            # Load metrics cards if loader available
            metrics_cards = []
            if self.metrics_loader:
                metrics_cards = self.metrics_loader.load_cards(detail_path)
            
            sections.append(UnifiedReportSection(
                title=title,
                content=content,
                metrics_cards=metrics_cards
            ))
        
        return sections
