
import pytest
import shutil
import os
from pathlib import Path
from typing import Generator

# Define the root of the sandbox environment relative to the project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
SANDBOX_DIR = PROJECT_ROOT / ".sandbox"

@pytest.fixture(scope="module", autouse=True)
def module_sandbox_cleanup(request):
    """
    Cleans up the sandbox directory for the entire test module before any tests run.
    This ensures we start with a clean slate for the module, removing artifacts 
    from previous runs or renamed tests.
    """
    # Calculate module path relative to tests/sandbox
    module_file = Path(request.module.__file__)
    try:
        # e.g tests/sandbox/unified_root/test_binding.py -> unified_root/test_binding
        rel_path = module_file.relative_to(PROJECT_ROOT / "tests" / "sandbox").with_suffix('')
    except ValueError:
        # Fallback if not inside tests/sandbox (e.g. running from slightly different context)
        rel_path = Path(module_file.stem)

    module_sandbox_path = SANDBOX_DIR / rel_path
    
    if module_sandbox_path.exists():
        try:
            # We use rmtree to delete the entire module folder
            shutil.rmtree(module_sandbox_path)
            print(f"Cleaned up sandbox module directory: {module_sandbox_path}")
        except Exception as e:
            print(f"Warning: Failed to cleanup sandbox module directory {module_sandbox_path}: {e}")

@pytest.fixture(scope="function")
def sandbox_root(request) -> Generator[Path, None, None]:
    """
    Creates a dedicated sandbox directory for the test function.
    
    Structure: sandbox/<relative_module_path>/<test_function_name>
    e.g. sandbox/unified_root/test_binding/test_function
    """
    # Calculate module path relative to tests/sandbox
    module_file = Path(request.module.__file__)
    try:
        rel_path = module_file.relative_to(PROJECT_ROOT / "tests" / "sandbox").with_suffix('')
    except ValueError:
        rel_path = Path(module_file.stem)
        
    test_name = request.node.name
    
    # Create the specific sandbox path
    # e.g. sandbox/unified_root/test_binding/test_default_structure
    test_sandbox_path = SANDBOX_DIR / rel_path / test_name
    
    if test_sandbox_path.exists():
        try:
            shutil.rmtree(test_sandbox_path)
        except Exception as e:
            print(f"Warning: file locking on Windows might prevent cleanup of {test_sandbox_path}: {e}")
            
    # Create the fresh directory
    test_sandbox_path.mkdir(parents=True, exist_ok=True)
    
    yield test_sandbox_path
    
    # specific cleanup logic if needed, but we explicitly want to KEEP artifacts
