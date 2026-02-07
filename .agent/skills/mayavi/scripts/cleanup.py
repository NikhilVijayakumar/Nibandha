import sys
import shutil
import sys
import shutil
from pathlib import Path

# Python 3.11+ has tomllib
try:
    import tomllib as toml
except ImportError:
    try:
        import tomli as toml
    except ImportError:
        print("❌ Error: neither 'tomllib' nor 'tomli' is installed. Cannot parse pyproject.toml.")
        sys.exit(1)

def cleanup_sandbox(root_path: Path):
    """
    Reads pyproject.toml to find the project name, constructs the temp path,
    and cleans it.
    """
    pyproject = root_path / "pyproject.toml"
    if not pyproject.exists():
        print("⚠️ pyproject.toml not found. Cannot determine Sandbox location.")
        return

    try:
        with open(pyproject, "rb") as f:
            data = toml.load(f)
        
        project_name = None
        # 1. Try standard project.name
        if "project" in data and "name" in data["project"]:
            project_name = data["project"]["name"]
            
        # 2. Try tool.poetry.name
        elif "tool" in data and "poetry" in data["tool"] and "name" in data["tool"]["poetry"]:
            project_name = data["tool"]["poetry"]["name"]

        if not project_name:
             print("⚠️ Could not determine project name from toml. Skipping cleanup.")
             return

        # Sanitize name
        project_name = project_name.replace("-", "_")
        
        # Construct Sandbox Path: .{ProjectName}/tmp  (e.g. .Nibandha/tmp)
        # Note: The rule says .{ProjectName}/tmp. 
        # But commonly we might have .Nibandha/Nibandha/tmp? 
        # The rule says: .{ProjectName}/tmp/
        
        sandbox_dir = root_path / f".{project_name}" / "tmp"
        
        if not sandbox_dir.exists():
            print(f"ℹ️ Sandbox directory '{sandbox_dir}' does not exist. Nothing to clean.")
            return

        print(f"🧹 Cleaning Sandbox: {sandbox_dir}")
        
        # Delete contents, not the dir itself (to keep permissions/existence)
        for item in sandbox_dir.iterdir():
            if item.is_file() or item.is_symlink():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
                
        print("✅ Sandbox cleaned.")

    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cleanup.py <project_root>")
        sys.exit(1)
        
    root = Path(sys.argv[1])
    cleanup_sandbox(root)
