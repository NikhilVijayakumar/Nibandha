import sys
import os
import tomli
from pathlib import Path

def get_forbidden_package_name(root_path: Path) -> str:
    """
    Reads pyproject.toml to find the project name.
    """
    pyproject = root_path / "pyproject.toml"
    if not pyproject.exists():
        print("⚠️ pyproject.toml not found. Cannot determine forbidden package.")
        return None

    try:
        with open(pyproject, "rb") as f:
            data = tomli.load(f)
        
        # 1. Try standard project.name
        if "project" in data and "name" in data["project"]:
            name = data["project"]["name"]
            return name.replace("-", "_")
            
        # 2. Try tool.poetry.name
        if "tool" in data and "poetry" in data["tool"] and "name" in data["tool"]["poetry"]:
            name = data["tool"]["poetry"]["name"]
            return name.replace("-", "_")

    except Exception as e:
        print(f"⚠️ Error reading pyproject.toml: {e}")
        
    return None

def verify_independence(agent_root: Path, forbidden_pkg: str):
    """
    Scans internal agent logic for forbidden imports.
    Excludes resources, examples, templates.
    """
    print(f"🔍 Audit Target: {agent_root}")
    print(f"🚫 Forbidden Package: '{forbidden_pkg}'")
    
    violations = []
    
    # Exclude directories where example code lives
    EXCLUDED_DIRS = {"resources", "examples", "templates"}
    
    for py_file in agent_root.rglob("*.py"):
        # Check if file path contains excluded dirs
        if any(excluded in py_file.parts for excluded in EXCLUDED_DIRS):
            continue
            
        try:
            content = py_file.read_text(encoding="utf-8").splitlines()
            for i, line in enumerate(content):
                clean_line = line.strip()
                if clean_line.startswith("#"):
                    continue # Skip comments
                    
                # Strict Import Ban
                # 1. import forbidden_pkg
                # 2. from forbidden_pkg import ...
                # 3. from x.forbidden_pkg import ...
                
                is_import = clean_line.startswith("import ")
                is_from = clean_line.startswith("from ")
                
                if not (is_import or is_from):
                    continue

                if f" {forbidden_pkg}" in clean_line or f".{forbidden_pkg}" in clean_line:
                     # Double check it's not a partial match like "nibandha_extra"
                     # The simplest check: does the token exist?
                     import_parts = clean_line.split()
                     if forbidden_pkg in import_parts:
                          violations.append(f"{py_file}:{i+1} -> Imported forbidden package '{forbidden_pkg}'")
                     # Check within dot notation: from nikhil.nibandha import ...
                     elif any(f".{forbidden_pkg}" in part or f"{forbidden_pkg}." in part for part in import_parts):
                          violations.append(f"{py_file}:{i+1} -> Imported forbidden package '{forbidden_pkg}'")

        except Exception as e:
            print(f"⚠️ Could not read {py_file}: {e}")

    if violations:
        print("❌ AGENT INDEPENDENCE VIOLATION!")
        for v in violations:
            print(f"  {v}")
        sys.exit(1)
    else:
        print("✅ The Agent is Clean and Independent.")
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_agent_independence.py <project_root>")
        sys.exit(1)
        
    root_path = Path(sys.argv[1])
    agent_path = root_path / ".agent"
    
    forbidden = get_forbidden_package_name(root_path)
    if not forbidden:
        sys.exit(0) # Pass if we can't determine what to forbid (warned above)
        
    verify_independence(agent_path, forbidden)
