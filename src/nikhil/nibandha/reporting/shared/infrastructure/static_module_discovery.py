from typing import List
from pathlib import Path
import logging

logger = logging.getLogger("nibandha.reporting")

class StaticModuleDiscovery:
    """
    Static implementation of module discovery that returns a pre-defined list of modules.
    Useful when you want to explicitly define which modules to analyze via configuration.
    """
    
    def __init__(self, modules: List[str]):
        """
        Initialize with a fixed list of modules.
        
        Args:
            modules: List of module names (e.g. ["Configuration", "Logging"])
        """
        self.modules = sorted([m.capitalize() for m in modules])
        
    def discover_modules(self, source_root: Path) -> List[str]:
        """
        Returns the statically configured list of modules, ignoring source_root scan.
        
        Args:
            source_root: Ignored in this implementation.
            
        Returns:
            The configured list of modules.
        """
        logger.debug(f"Using static module list: {self.modules}")
        return self.modules
