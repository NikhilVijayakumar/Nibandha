import ast
import os
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple
import logging

logger = logging.getLogger("nibandha.reporting.quality.hygiene")

class HygieneVisitor(ast.NodeVisitor):
    def __init__(self, filename: str):
        self.filename = filename
        self.magic_numbers: List[Tuple[int, int, int]] = [] # line, col, value
        self.hardcoded_paths: List[Tuple[int, int, str]] = [] # line, col, value
        self.forbidden_functions: List[Tuple[int, int, str]] = [] # line, col, name
        
        from ...shared.constants import HYGIENE_FORBIDDEN_NAMES
        self.forbidden_names = HYGIENE_FORBIDDEN_NAMES
        self.source_code = ""  # Will be set by caller
        self._docstring_lines: Set[int] = set()  # Track lines inside docstrings

    def _is_in_docstring(self, lineno: int) -> bool:
        """Check if a line number is inside a docstring."""
        if not self.source_code:
            return False
        
        # Simple heuristic: check if line is part of a triple-quoted string
        lines = self.source_code.split('\n')
        if lineno > len(lines):
            return False
        
        line = lines[lineno - 1].strip()
        # Check if this line or nearby lines have triple quotes
        for offset in range(-2, 3):  # Check 2 lines before and after
            check_line = lineno + offset
            if 1 <= check_line <= len(lines):
                check_content = lines[check_line - 1]
                if '"""' in check_content or "'''" in check_content:
                    return True
        return False

    def visit_Constant(self, node: ast.Constant) -> None:
        from ...shared.constants import HYGIENE_IGNORED_NUMBERS, HYGIENE_MIN_PATH_LENGTH
        
        # Skip if inside docstring
        if self._is_in_docstring(node.lineno):
            return
        
        if isinstance(node.value, (int, float)):
            if node.value not in HYGIENE_IGNORED_NUMBERS and not isinstance(node.value, bool): 
                 self.magic_numbers.append((node.lineno, node.col_offset, node.value))
        
        if isinstance(node.value, str):
            # More restrictive path detection to reduce false positives
            has_slash = "/" in node.value or "\\" in node.value
            is_long_enough = len(node.value) > HYGIENE_MIN_PATH_LENGTH
            
            # Must look like an actual filesystem path (not just contain slashes)
            looks_like_path = (
                has_slash and is_long_enough and
                # Exclude URLs, format strings, regex patterns, newlines
                not any(x in node.value for x in ["http://", "https://", "<", ">", "%", "\\n", "\\t", "\\[", "\\]", "\\("]) and
                # Must start with common path patterns
                (node.value.startswith("/") or node.value.startswith("../") or node.value.startswith("./") or 
                 node.value.startswith("src/") or node.value.startswith("docs/") or node.value.startswith("tests/") or
                 node.value.startswith("logs/") or ".Nibandha/" in node.value or "assets/images" in node.value)
            )
            
            if looks_like_path:
                 self.hardcoded_paths.append((node.lineno, node.col_offset, node.value))
    
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name):
            if node.func.id in self.forbidden_names:
                self.forbidden_functions.append((node.lineno, node.col_offset, node.func.id))
        elif isinstance(node.func, ast.Attribute):
            name = node.func.attr
            if name in self.forbidden_names:
                 self.forbidden_functions.append((node.lineno, node.col_offset, name))
        self.generic_visit(node)

class HygieneReporter:
    def __init__(self, source_root: Path):
        self.source_root = source_root

    def run(self) -> Dict[str, Any]:
        """
        Scans codebase for hygiene issues.
        Returns dictionary with violations.
        """
        violations = {
            "magic_numbers": [],
            "hardcoded_paths": [],
            "forbidden_functions": []
        }
        
        count = 0
        
        for root, dirs, files in os.walk(self.source_root):
            # Skip common ignores
            if "__pycache__" in root or ".venv" in root or ".git" in root or "build" in root or "dist" in root:
                continue
                
            for file in files:
                if not file.endswith(".py"):
                    continue
                
                # Skip constants files - they DEFINE constants, not misuse them
                if file in ("constants.py", "visualizer_constants.py"):
                    continue
                    
                path = Path(root) / file
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        source_code = f.read()
                        tree = ast.parse(source_code, filename=str(path))
                    
                    visitor = HygieneVisitor(str(path))
                    visitor.source_code = source_code  # Pass source for docstring detection
                    visitor.visit(tree)
                    
                    rel_path = str(path.relative_to(self.source_root))
                    
                    for line, col, val in visitor.magic_numbers:
                        violations["magic_numbers"].append({
                            "file": rel_path, "line": line, "value": val
                        })
                        count += 1
                        
                    for line, col, val in visitor.hardcoded_paths:
                        violations["hardcoded_paths"].append({
                            "file": rel_path, "line": line, "value": val
                        })
                        count += 1

                    for line, col, val in visitor.forbidden_functions:
                         violations["forbidden_functions"].append({
                            "file": rel_path, "line": line, "value": val
                        })
                         count += 1

                except Exception as e:
                    logger.warning(f"Failed to parse {path}: {e}")

        return {
            "status": "PASS" if count == 0 else "FAIL",
            "violation_count": count,
            "details": violations
        }
