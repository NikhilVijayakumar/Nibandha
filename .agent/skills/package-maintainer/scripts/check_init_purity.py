import ast
import sys
from pathlib import Path


def is_init_pure(file_path: Path):
    """
    Checks if an __init__.py file contains prohibited logic.
    Allowed: Imports, __version__ assignments, and __all__ lists.
    Prohibited: Function definitions, Class definitions, and complex logic.
    """
    try:
        tree = ast.parse(file_path.read_text())
    except SyntaxError:
        print(f"❌ {file_path}: Syntax error in file.")
        return False

    violations = []
    for node in tree.body:
        # Ignore Docstrings
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue

        # Allow Imports
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            continue

        # Allow simple assignments (like __version__ or __all__)
        if isinstance(node, ast.Assign):
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id in ["__version__", "__all__"]:
                continue
            violations.append(f"Unexpected assignment: {target.id}")

        # Prohibit Classes
        if isinstance(node, ast.ClassDef):
            violations.append(f"Class definition found: {node.name}")

        # Prohibit Functions
        if isinstance(node, ast.FunctionDef):
            violations.append(f"Function definition found: {node.name}")

    if violations:
        print(f"❌ Purity Violation in {file_path}:")
        for v in violations:
            print(f"  - {v}")
        return False

    return True


def run_purity_audit(src_dir: str = "src"):
    root = Path(src_dir)
    all_pure = True

    print(f"🕵️  Auditing __init__.py purity in {src_dir}...")

    for init_file in root.glob("**/__init__.py"):
        if not is_init_pure(init_file):
            all_pure = False

    if all_pure:
        print("✅ All __init__.py files are pure (Gatekeepers only).")
    return all_pure


if __name__ == "__main__":
    success = run_purity_audit()
    sys.exit(0 if success else 1)