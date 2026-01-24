"""
Protocol for module discovery in project structures.

This protocol allows clients to provide custom logic for discovering
code modules in their projects, enabling support for various architectures
(e.g., Clean Architecture, Django apps, microservices).
"""

from typing import Protocol, List
from pathlib import Path


class ModuleDiscoveryProtocol(Protocol):
    """
    Protocol for discovering code modules in a project.
    
    Implementations should scan a source directory and return a list
    of module names. Module names should be human-readable strings
    (e.g., "Configuration", "Logging", "Reporting").
    
    Example:
        >>> class MyDiscovery:
        ...     def discover_modules(self, source_root: Path) -> List[str]:
        ...         return ["Auth", "Users", "Payments"]
        >>> 
        >>> discovery = MyDiscovery()
        >>> modules = discovery.discover_modules(Path("src"))
        ['Auth', 'Users', 'Payments']
    """
    
    def discover_modules(self, source_root: Path) -> List[str]:
        """
        Discover all top-level modules in the project.
        
        Args:
            source_root: Root directory to scan for modules
            
        Returns:
            List of module names in a human-readable format
            (e.g., ["Configuration", "Logging", "Reporting"])
            
        Note:
            Module names should be capitalized for consistency in reports.
            The implementation should filter out Python internals like
            __pycache__, __init__.py, etc.
        """
        ...
