import sys
from pathlib import Path


def verify_package_imports(directory: str, package_prefix: str = "nikhil.nibandha"):
    """
    Scans for relative imports and ensures all internal links use the
    absolute package prefix.
    """
    root = Path(directory)
    violations = []

    for py_file in root.glob("**/*.py"):
        if py_file.name == "__init__.py":
            continue

        content = py_file.read_text().splitlines()
        for i, line in enumerate(content):
            clean_line = line.strip()

            # Rule: No Relative Imports
            if clean_line.startswith("from .") or clean_line.startswith("import ."):
                violations.append(f"{py_file}:{i + 1} -> Relative import detected.")

            # Rule: Absolute Pathing for internal modules
            # If importing 'nibandha' it MUST be prefixed with 'nikhil.'
            if "from nibandha" in clean_line or "import nibandha" in clean_line:
                violations.append(f"{py_file}:{i + 1} -> Missing 'nikhil' prefix in absolute import.")

    if violations:
        print(f"❌ Import Violations Found in '{directory}':")
        for v in violations:
            print(f"  {v}")
        return False

    print(f"✅ All imports in '{directory}' satisfy the Constitution.")
    return True


if __name__ == "__main__":
    # Check both source and tests
    src_valid = verify_package_imports("src")
    test_valid = verify_package_imports("tests")

    if not (src_valid and test_valid):
        sys.exit(1)