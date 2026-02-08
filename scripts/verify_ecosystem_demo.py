import os
import sys
import shutil
import subprocess
from pathlib import Path

def print_tree(directory, prefix=""):
    """Recursively prints the directory tree structure."""
    if not directory.exists():
        print(f"{prefix}[Missing Directory]")
        return

    items = sorted([i for i in directory.iterdir() if i.name != "__pycache__" and i.name != ".pytest_cache"])
    pointers = [("|-- " if i < len(items) - 1 else "+-- ") for i in range(len(items))]

    for pointer, item in zip(pointers, items):
        print(f"{prefix}{pointer}{item.name}{'/' if item.is_dir() else ''}")
        if item.is_dir():
            print_tree(item, prefix + ("|   " if pointer == "|-- " else "    "))

def main():
    print("\n=== Ecosystem Single-Config Demonstration ===\n")
    
    # 1. Setup Sandbox Path
    base_dir = Path.cwd()
    sandbox_dir = base_dir / ".sandbox"
    
    # 2. Run the specific test using pytest
    test_file = "tests/sandbox/unified_root/ecosystem/test_practical_single_config.py"
    # Force PYTHONIOENCODING=utf-8 for the subprocess to handle any remaining unicode in pytest output
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    cmd = [sys.executable, "-m", "pytest", test_file, "-v", "-s"]
    
    print(f"Running Test: {test_file}...")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", env=env)
    
    if result.returncode != 0:
        print("\n[X] Test Failed!")
        # Sanitize output before printing to avoid crash in parent process
        try:
            print(result.stdout)
            print(result.stderr)
        except UnicodeEncodeError:
            print(result.stdout.encode('ascii', 'replace').decode())
            print(result.stderr.encode('ascii', 'replace').decode())
        sys.exit(1)
    
    print("[OK] Test Passed!\n")
    
    # 3. Inspect the Generated Structure
    target_root = sandbox_dir / "unified_root" / "ecosystem" / "test_practical_single_config" / "test_single_config_multi_library_organization" / "Practical_Single_Config_Multi_Lib" / ".Pravaha"
    
    if not target_root.exists():
        # Fallback: check if it's directly under the function name folder (current behavior observed)
        target_root = sandbox_dir / "unified_root" / "ecosystem" / "test_practical_single_config" / "test_single_config_multi_library_organization" / ".Pravaha"
    
    if not target_root.exists():
        print(f"[X] Error: Could not find generated root at {target_root}")
        target_root_akashvani = sandbox_dir / "unified_root" / "ecosystem" / "test_practical_single_config" / "Practical_Akashvani_Ecosystem" / ".Akashvani"
        if target_root_akashvani.exists():
             target_root = target_root_akashvani
             print(f"Found Akashvani root instead at {target_root}")
        else:
             sys.exit(1)

    print(f"Generated Structure at: {target_root}\n")
    try:
        print(f"{target_root.name}/")
        print_tree(target_root)
    except UnicodeEncodeError:
         print("Error printing tree due to encoding.")

    print("\n=============================================")

if __name__ == "__main__":
    main()
