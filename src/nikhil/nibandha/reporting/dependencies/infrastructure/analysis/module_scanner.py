"""
Module Dependency Scanner.
"""

import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class ModuleScanner:
    """Scans source code to build module import graph."""
    
    def __init__(self, source_root: Path, package_roots: List[str] = None):
        """
        Args:
            source_root: Path to source code root.
            package_roots: List of root package names to identify internal dependencies (e.g. ['nikhil', 'pravaha', 'nibandha']).
        """
        self.source_root = source_root
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.module_files: Dict[str, Path] = {}
        self.package_roots = package_roots or []
        
    def scan(self) -> Dict[str, Set[str]]:
        """Scan all Python files and build dependency graph."""
        # Find all Python files
        for py_file in self.source_root.rglob("*.py"):
            if "__pycache__" in str(py_file) or ".venv" in str(py_file) or "test" in str(py_file):
                continue
                
            module_name = self._get_module_name(py_file)
            if module_name == "Root":
                continue

            self.module_files[module_name] = py_file
            
            # Extract imports
            imports = self._extract_imports(py_file)
            self.dependencies[module_name] = imports
        
        # Filter to only internal dependencies
        self._filter_internal_dependencies()
        
        return dict(self.dependencies)
    
    def _get_module_name(self, file_path: Path) -> str:
        """Convert file path to module name."""
        try:
            rel_path = file_path.relative_to(self.source_root)
        except ValueError:
            return file_path.stem.capitalize()
        
        # Remove .py extension
        parts = list(rel_path.parts[:-1]) + [rel_path.stem]
        
        # Skip __init__
        if parts and parts[-1] == "__init__":
            parts = parts[:-1]
            
        if not parts:
            return "Root"

        if len(parts) > 0:
            return parts[0].capitalize()
            
        return "Unknown"
    
    def _extract_imports(self, file_path: Path) -> Set[str]:
        """Parse file and extract import statements."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(file_path))
        except Exception:
            return set()
        
        imports = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split(".")[0]
                    imports.add(module)
                    
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    parts = node.module.split(".")
                    # Check if it matches any package root
                    is_internal = False
                    for root in self.package_roots:
                        if root in parts:
                            is_internal = True
                            break
                    
                    if is_internal:
                        # Extract root module only (e.g., nikhil.pravaha.logging.domain... -> Logging)
                        # We need to find the segment after the package root.
                        # Assuming package root is like 'nikhil.nibandha'
                        for root in self.package_roots:
                            root_parts = root.split(".")
                            # If parts starts with root_parts
                            if parts[:len(root_parts)] == root_parts:
                                if len(parts) > len(root_parts):
                                    imports.add(parts[len(root_parts)].capitalize())
                                break

        return imports
    
    def _filter_internal_dependencies(self):
        """Keep only dependencies to modules we know about."""
        known_modules = set(self.module_files.keys())
        
        for module in self.dependencies:
            self.dependencies[module] = {
                dep for dep in self.dependencies[module]
                if dep in known_modules and dep != module
            }
    
    def find_circular_dependencies(self) -> List[Tuple[str, str]]:
        circular = []
        for module_a in self.dependencies:
            for module_b in self.dependencies[module_a]:
                if module_a in self.dependencies.get(module_b, set()):
                    pair = tuple(sorted([module_a, module_b]))
                    if pair not in circular:
                        circular.append(pair)
        return circular
    
    def get_most_imported(self, top_n: int = 5) -> List[Tuple[str, int]]:
        import_counts = defaultdict(int)
        for deps in self.dependencies.values():
            for dep in deps:
                import_counts[dep] += 1
        return sorted(import_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    def get_most_dependent(self, top_n: int = 5) -> List[Tuple[str, int]]:
        return sorted(
            [(mod, len(deps)) for mod, deps in self.dependencies.items()],
            key=lambda x: x[1], reverse=True
        )[:top_n]
    
    def get_isolated_modules(self) -> List[str]:
        all_modules = set(self.dependencies.keys())
        depended_upon = set()
        for deps in self.dependencies.values():
            depended_upon.update(deps)
            
        isolated = []
        for module in all_modules:
            if len(self.dependencies[module]) == 0 and module not in depended_upon:
                isolated.append(module)
        return isolated
