"""Helper class for discovering and filtering markdown files for export."""
import logging
from pathlib import Path
from typing import List

from nibandha.configuration.domain.models.export_config import ExportConfig

logger = logging.getLogger("nibandha.export.helpers")


class FileDiscovery:
    """
    Discovers and filters markdown files for export.
    
    Responsibilities:
    - Find markdown files in input directory
    - Apply exclusion filters
    - Apply custom ordering (or alphabetic default)
    """
    
    def __init__(self, config: ExportConfig):
        """
        Initialize with export configuration.
        
        Args:
            config: ExportConfig with input_dir, export_order, and exclude_files
        """
        self.config = config
    
    def discover_files(self) -> List[Path]:
        """
        Discover markdown files according to configuration.
        
        Returns:
            List of markdown file paths in specified order, with exclusions applied
            
        Raises:
            ValueError: If input_dir is not configured or doesn't exist
        """
        if not self.config.input_dir:
            logger.error("Cannot discover files: input_dir not configured")
            raise ValueError("input_dir must be configured for file discovery")
        
        if not self.config.input_dir.exists():
            logger.error(f"Input directory not found: {self.config.input_dir}")
            raise ValueError(f"input_dir does not exist: {self.config.input_dir}")
        
        # Find all markdown files
        all_markdown_files = list(self.config.input_dir.glob("*.md"))
        
        if not all_markdown_files:
            logger.warning(f"No markdown files found in {self.config.input_dir}")
            return []
        
        # Apply exclusions
        filtered_files = self._apply_exclusions(all_markdown_files)
        
        # Apply ordering
        ordered_files = self._apply_ordering(filtered_files)
        
        logger.info(f"Discovered {len(ordered_files)} markdown files for export")
        return ordered_files
    
    def _apply_exclusions(self, files: List[Path]) -> List[Path]:
        """
        Filter out excluded files.
        
        Args:
            files: List of all markdown files
            
        Returns:
            Filtered list with exclusions removed
        """
        if not self.config.exclude_files:
            return files
        
        excluded_stems = set(self.config.exclude_files)
        filtered = [f for f in files if f.stem not in excluded_stems]
        
        excluded_count = len(files) - len(filtered)
        if excluded_count > 0:
            logger.info(f"Excluded {excluded_count} file(s) from export")
        
        return filtered
    
    def _apply_ordering(self, files: List[Path]) -> List[Path]:
        """
        Order files according to configuration.
        
        Args:
            files: List of filtered markdown files
            
        Returns:
            Ordered list of files
        """
        if not self.config.export_order:
            # Default: alphabetic by filename
            ordered = sorted(files, key=lambda f: f.stem.lower())
            logger.debug("Using alphabetic file ordering")
            return ordered
        
        # Custom ordering
        order_map = {stem: idx for idx, stem in enumerate(self.config.export_order)}
        file_map = {f.stem: f for f in files}
        
        # Split into ordered and unordered
        ordered_files = []
        unordered_files = []
        
        for file in files:
            if file.stem in order_map:
                ordered_files.append(file)
            else:
                unordered_files.append(file)
        
        # Sort ordered files by specified order
        ordered_files.sort(key=lambda f: order_map[f.stem])
        
        # Append unordered files alphabetically
        unordered_files.sort(key=lambda f: f.stem.lower())
        
        result = ordered_files + unordered_files
        
        logger.debug(f"Applied custom ordering: {len(ordered_files)} ordered, {len(unordered_files)} unordered")
        return result
