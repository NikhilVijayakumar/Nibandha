#!/usr/bin/env python3
"""
Sandbox Test Runner Script

Usage:
    python scripts/run_sandbox.py [module_name] [--clean]

Description:
    Runs sandbox tests for specified modules or all modules if none specified.
    Supports dynamic discovery of test modules in tests/sandbox.
    Optionally cleans up artifacts before running.

Examples:
    python scripts/run_sandbox.py                 # Run all sandbox tests
    python scripts/run_sandbox.py configuration   # Run configuration tests only
    python scripts/run_sandbox.py configuration --clean # Clean artifacts then run
"""

import argparse
import sys
import shutil
import subprocess
from pathlib import Path
from typing import List

# Setup paths relative to script location
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
TESTS_SANDBOX_DIR = PROJECT_ROOT / "tests" / "sandbox"
SANDBOX_OUTPUT_DIR = PROJECT_ROOT / ".sandbox"

def get_available_modules() -> List[str]:
    """
    Dynamically discover available sandbox test modules.
    A valid module is a subdirectory in tests/sandbox that isn't __pycache__ or starting with dot.
    """
    if not TESTS_SANDBOX_DIR.exists():
        print(f"Error: Sandbox test directory not found at {TESTS_SANDBOX_DIR}")
        return []
    
    modules = []
    for item in TESTS_SANDBOX_DIR.iterdir():
        if item.is_dir() and not item.name.startswith((".", "__")):
            # Check if it contains tests (rough check)
            if list(item.glob("test_*.py")) or list(item.glob("**/test_*.py")):
                modules.append(item.name)
    return sorted(modules)

def clean_sandbox(module: str = None):
    """Clean the .sandbox artifact directory."""
    if not SANDBOX_OUTPUT_DIR.exists():
        return

    if module:
        target = SANDBOX_OUTPUT_DIR / module
        if target.exists():
            print(f"Cleaning artifacts for module: {module}...")
            shutil.rmtree(target)
    else:
        print("Cleaning ALL sandbox artifacts...")
        # Clean everything but keep the directory
        for item in SANDBOX_OUTPUT_DIR.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

def run_tests(modules: List[str]):
    """Run pytest for the specified modules."""
    for module in modules:
        print(f"\n{'='*20} Running Sandbox Module: {module} {'='*20}")
        target_path = TESTS_SANDBOX_DIR / module
        
        cmd = [sys.executable, "-m", "pytest", str(target_path), "-v", "--tb=short"]
        
        try:
            result = subprocess.run(cmd, cwd=PROJECT_ROOT, check=False)
            if result.returncode != 0:
                print(f"❌ Module '{module}' failed check output above.")
                # We continue to next module even if one fails
            else:
                print(f"✅ Module '{module}' passed.")
        except Exception as e:
            print(f"Error running tests for {module}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Run sandbox tests for Nibandha.")
    parser.add_argument("module", nargs="?", help="Specific module to run (e.g., configuration). Runs all if omitted.")
    parser.add_argument("--clean", action="store_true", help="Clean sandbox artifacts before running.")
    parser.add_argument("--list", action="store_true", help="List available modules.")
    
    args = parser.parse_args()
    
    available_modules = get_available_modules()
    
    if args.list:
        print("Available Sandbox Modules:")
        for m in available_modules:
            print(f" - {m}")
        return

    # Validate module argument
    target_modules = []
    if args.module:
        if args.module not in available_modules:
            print(f"Error: Module '{args.module}' not found in {TESTS_SANDBOX_DIR}")
            print("Available modules:", ", ".join(available_modules))
            sys.exit(1)
        target_modules = [args.module]
    else:
        target_modules = available_modules

    if not target_modules:
        print("No sandbox modules found to run.")
        return

    # Clean if requested (or maybe always for specific module runs? User prompt implied manual clean)
    if args.clean:
        if args.module:
            clean_sandbox(args.module)
        else:
            clean_sandbox()

    print(f"Starting Sandbox Run for: {', '.join(target_modules)}")
    run_tests(target_modules)
    
    print(f"\nArtifacts generated in: {SANDBOX_OUTPUT_DIR}")

if __name__ == "__main__":
    main()
