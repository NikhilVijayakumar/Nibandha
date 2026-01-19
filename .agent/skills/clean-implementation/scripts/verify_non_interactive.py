import ast
import sys
from pathlib import Path


def verify_headless_compliance(directory: str):
    root = Path(directory)
    violations = []

    for py_file in root.glob("**/*.py"):
        tree = ast.parse(py_file.read_text())

        for node in ast.walk(tree):
            # Check for input() calls
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == "input":
                    violations.append(f"❌ {py_file}: Interactive 'input()' found. Violation of Rule 3.")

            # Check for direct open() with hardcoded strings (suggests bypassing settings)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == "open" and isinstance(node.args[0], ast.Constant):
                    if not str(node.args[0]).endswith(".py"):  # Ignore self-reads if any
                        violations.append(f"⚠️ {py_file}: Hardcoded file path in open(). Use self.settings instead.")

    if violations:
        for v in violations: print(v)
        return False
    return True


if __name__ == "__main__":
    if not verify_headless_compliance("src"):
        sys.exit(1)