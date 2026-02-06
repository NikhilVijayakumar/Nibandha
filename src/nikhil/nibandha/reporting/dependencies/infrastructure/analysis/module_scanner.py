"""
Module Dependency Scanner.
"""

import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict

class ModuleScanner:
    """Scans source code to build module import graph."""
    
    def __init__(self, source_root: Path, package_roots: Optional[List[str]] = None):
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
        from nibandha.reporting.shared.constants import SCANNER_EXCLUSIONS
        
        exclusions = SCANNER_EXCLUSIONS
        
        # Find all Python files
        for py_file in self.source_root.rglob("*.py"):
            # Internal optimization: check parts for faster exclusion
            if any(ex in py_file.parts for ex in exclusions):
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
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                tree = ast.parse(f.read(), filename=str(file_path))
        except Exception:
            return set()
        
        return self._extract_imports_from_tree(tree)


    def _extract_imports_from_tree(self, tree: ast.AST) -> Set[str]:
        imports: Set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                self._process_import_node(node, imports)
            elif isinstance(node, ast.ImportFrom):
                self._process_import_from_node(node, imports)
        return imports

    def _process_import_node(self, node: ast.Import, imports: Set[str]) -> None:
        for alias in node.names:
            parts = alias.name.split(".")
            found = False
            
            # Internal Check
            for root in self.package_roots:
                root_parts = root.split(".")
                if parts[:len(root_parts)] == root_parts:
                    if len(parts) > len(root_parts):
                        imports.add(parts[len(root_parts)].capitalize())
                    found = True
                    break
            
            # External Check
            if not found:
                imports.add(parts[0])

    def _process_import_from_node(self, node: ast.ImportFrom, imports: Set[str]) -> None:
        if not node.module: return
        
        parts = node.module.split(".")
        found = False
        
        # Internal Check
        for root in self.package_roots:
            root_parts = root.split(".")
            if parts[:len(root_parts)] == root_parts:
                if len(parts) > len(root_parts):
                    imports.add(parts[len(root_parts)].capitalize())
                found = True
                break
        
        if not found: return

        # Extract root module (e.g., nikhil.pravaha.logging.domain... -> Logging)
        for root in self.package_roots:
            root_parts = root.split(".")
            # If parts starts with root_parts
            if parts[:len(root_parts)] == root_parts:
                if len(parts) > len(root_parts):
                    imports.add(parts[len(root_parts)].capitalize())
                break
    
    def _filter_internal_dependencies(self) -> None:
        """Keep only dependencies to modules we know about."""
        known_modules = set(self.module_files.keys())
        
        for module in self.dependencies:
            self.dependencies[module] = {
                dep for dep in self.dependencies[module]
                if dep in known_modules and dep != module
            }
    
    def find_circular_dependencies(self) -> List[Tuple[str, str]]:
        circular: List[Tuple[str, str]] = []
        for module_a in self.dependencies:
            for module_b in self.dependencies[module_a]:
                if module_a in self.dependencies.get(module_b, set()):
                    pair = (min(module_a, module_b), max(module_a, module_b))
                    if pair not in circular:
                        circular.append(pair)
        return circular
    
    def get_most_imported(self, top_n: int = 5) -> List[Tuple[str, int]]:
        import_counts: Dict[str, int] = defaultdict(int)
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
