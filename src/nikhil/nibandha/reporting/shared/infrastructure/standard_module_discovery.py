"""
Standard implementation of module discovery.

This implementation works for typical Python packages where modules
are organized as top-level subdirectories under a source root.
"""

from pathlib import Path
from typing import List, Optional
import logging

logger = logging.getLogger("nibandha.reporting")


class StandardModuleDiscovery:
    """
    Standard module discovery that scans for top-level directories.
    
    This implementation works for typical Python package structures where
    each module is a subdirectory containing Python files.
    
    Example structure:
        src/mypackage/
        ├── configuration/
        ├── logging/
        ├── reporting/
        └── utils/
        
    Would discover: ["Configuration", "Logging", "Reporting", "Utils"]
    """
    
    def __init__(self, exclude_patterns: Optional[List[str]] = None):
        """
        Initialize the standard module discovery.
        
        Args:
            exclude_patterns: Optional list of directory names to exclude
                             (e.g., ["__pycache__", "tests", ".git"])
        """
        self.exclude_patterns = exclude_patterns or [
            "__pycache__",
            "__init__",
            ".git",
            ".pytest_cache",
            "dist",
            "build",
            "egg-info"
        ]
    
    def discover_modules(self, source_root: Path) -> List[str]:
        """
        Discover modules by scanning for top-level directories.
        
        Args:
            source_root: Root directory to scan for modules
            
        Returns:
            Sorted list of capitalized module names
        """
        if not source_root.exists():
            logger.warning(f"Source root does not exist: {source_root}")
            return []
        
        if not source_root.is_dir():
            logger.warning(f"Source root is not a directory: {source_root}")
            return []
        
        modules = []
        
        try:
            for item in source_root.iterdir():
                # Skip non-directories
                if not item.is_dir():
                    continue
                
                # Skip excluded patterns
                if item.name in self.exclude_patterns:
                    continue
                
                # Skip hidden directories
                if item.name.startswith("."):
                    continue
                
                # Skip names starting with __
                if item.name.startswith("__"):
                    continue
                
                # Add capitalized module name
                modules.append(item.name.capitalize())
            
            logger.debug(f"Discovered {len(modules)} modules in {source_root}: {modules}")
            return sorted(modules)
            
        except Exception as e:
            logger.error(f"Error discovering modules in {source_root}: {e}")
            return []
