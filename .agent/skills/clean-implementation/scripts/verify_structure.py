import os
import ast
from pathlib import Path


def audit_ddd_structure(src_root: str):
    root = Path(src_root)
    errors = []

    for py_file in root.glob("**/*.py"):
        if py_file.name == "__init__.py": continue

        with open(py_file, "r") as f:
            tree = ast.parse(f.read())

        classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]

        # Rule 1: One Class, One File
        if len(classes) > 1:
            errors.append(f"❌ {py_file}: Multiple classes found. (Expected: 1)")

        # Rule 2: No Nested Functions/Classes
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for sub_node in node.body:
                    if isinstance(sub_node, (ast.ClassDef, ast.FunctionDef)):
                        errors.append(f"❌ {py_file}: Nested structure detected in '{node.name}'.")

    if errors:
        for err in errors: print(err)
        return False
    return True


if __name__ == "__main__":
    audit_ddd_structure("src/nibandha/domain/models")