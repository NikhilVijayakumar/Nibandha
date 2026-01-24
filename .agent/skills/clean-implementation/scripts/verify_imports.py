import sys
import tomli
from pathlib import Path


def get_project_package_name(root_path: Path) -> str:
    """
    Attempts to detect the project package name from pyproject.toml.
    Returns None if not found.
    """
    pyproject = root_path / "pyproject.toml"
    if not pyproject.exists():
        return None
        
    try:
        with open(pyproject, "rb") as f:
            data = tomli.load(f)
            
        # Try standard locations
        # [project] name = "..."
        if "project" in data and "name" in data["project"]:
             name = data["project"]["name"]
             # If name is like "my-package", python package is often "my_package"
             return name.replace("-", "_")
             
        # [tool.poetry] name = "..."
        if "tool" in data and "poetry" in data["tool"] and "name" in data["tool"]["poetry"]:
             name = data["tool"]["poetry"]["name"]
             return name.replace("-", "_")
             
    except Exception:
        pass
        
    return None

def verify_package_imports(directory: str, package_prefix: str = None):
    """
    Scans for relative imports and ensures all internal links use the
    absolute package prefix.
    """
    root = Path(directory)
    project_root = root.parent # Assuming src/ or tests/ is inside project root
    
    if not package_prefix:
        package_prefix = get_project_package_name(project_root)
        
    if not package_prefix:
        # Fallback or strict error? 
        # Let's try to guess from the first non-init directory in src if exists
        # Or just warn.
        print("⚠️  Could not detect package name. Using strict absolute check without prefix validation.")
    else:
        print(f"🔍 Validating absolute imports for package: '{package_prefix}'")

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
            # If we know the prefix, strict check it.
            if package_prefix:
                # If importing from the package_prefix (e.g. "from my_pkg...")
                # We want to ensure they ARE using it.
                # Actually the rule meant: if you import something that belongs to THIS project, use absolute path.
                # So if I am in 'src/my_pkg/a.py' and I import 'b', I should do 'from my_pkg import b'
                
                # Heuristic: If line contains "import <package_prefix>" or "from <package_prefix>" it's good (absolute).
                # But if it imports a sibling without prefix? "import sibling" -> That's standard absolute but internal.
                # The rule specifically targeted avoiding "from . import x" (caught above) 
                # AND avoiding "import x" where x is local module? No, Python 3 makes "import x" absolute.
                # So mostly we focus on ensuring they don't use short aliases if a multi-part prefix exists?
                # The logic in previous script was: if "from nibandha" ensure "nikhil." prefix.
                # This handles the namespace package case.
                
                # General logic: If we detect the *unprefixed* part of a known complex namespace, flag it.
                # e.g. if package is 'foo.bar', and we see "from bar import...", flag it.
                if "." in package_prefix:
                    root_ns, sub_ns = package_prefix.split(".", 1)
                    # If we see import sub_ns without root_ns
                    if f"from {sub_ns}" in clean_line or f"import {sub_ns}" in clean_line:
                         # But be careful if it's part of the full string
                         if package_prefix not in clean_line:
                             violations.append(f"{py_file}:{i + 1} -> Missing '{root_ns}' prefix in absolute import.")
            
            # Rule: Architectural Boundaries (Domain cannot import Infrastructure or Application)
            # Check if current file is in domain layer
            if "domain" in str(py_file):
                if "infrastructure" in clean_line:
                     violations.append(f"{py_file}:{i + 1} -> ARCHITECTURE VIOLATION: Domain layer importing Infrastructure.")
                if "application" in clean_line:
                     violations.append(f"{py_file}:{i + 1} -> ARCHITECTURE VIOLATION: Domain layer importing Application.")

    if violations:
        print(f"❌ Import Violations Found in '{directory}':")
        for v in violations:
            print(f"  {v}")
        return False

    print(f"✅ All imports in '{directory}' satisfy the Constitution.")
    return True


if __name__ == "__main__":
    # Check both source and tests
    # Allow override via args
    prefix = sys.argv[1] if len(sys.argv) > 1 else None
    
    src_valid = verify_package_imports("src", prefix)
    test_valid = verify_package_imports("tests", prefix)

    if not (src_valid and test_valid):
        sys.exit(1)