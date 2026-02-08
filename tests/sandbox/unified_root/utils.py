
import os
import shutil
import pytest
from pathlib import Path
from typing import Callable, Optional
from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.configuration.infrastructure.file_loader import FileConfigLoader
from nibandha.unified_root.infrastructure.filesystem_binder import FileSystemBinder
from nibandha.unified_root.domain.models.root_context import RootContext

# Base Template provided by User
BASE_CONFIG_TEMPLATE = {
    "name": "Nibandha",
    "mode": "production",
    "logging": {
        "level": "INFO",
        "enabled": True,
        "log_dir": ".Nibandha/logs",
        "rotation": {  # Nested rotation structure
            "enabled": False,
            "max_size_mb": 5.0,
            "rotation_interval_hours": 24,
            "archive_retention_days": 30,
            "backup_count": 10,
            "archive_dir": "logs/archive",
            "timestamp_format": "%Y-%m-%d"
        }
    },
    "reporting": {
        "output_dir": ".Nibandha/Report",
        "template_dir": "src/nikhil/nibandha/reporting/templates",
        "project_name": "Nibandha",
        "quality_target": "src/nikhil",
        "package_roots": ["nibandha"],
        "unit_target": "tests/unit",
        "e2e_target": "tests/e2e",
        "doc_paths": {
            "functional": "docs/features",
            "technical": "docs/technical",
            "test": "docs/test"
        },
        "module_discovery": None
    },
    "unified_root": {
        "name": ".Nibandha",
        "custom_structure": {}
    },
    "export": {
        "formats": ["md", "html"],
        "style": "default",
        "input_dir": ".Nibandha/Report/details",
        "template_dir": "src/nikhil/nibandha/export/infrastructure/templates",
        "styles_dir": "src/nikhil/nibandha/export/infrastructure/styles",
        "output_dir": ".Nibandha/Nibandha/Report",
        "output_filename": "report",
        "exclude_files": [],
        "metrics_mapping": {}
    }
}

def run_ur_test(
    sandbox_path: Path,
    test_name: str,
    description: str,
    input_config_content: str,
    expected_output_desc: str,
    validation_fn: Callable[[RootContext, Path], None],
    use_rotation: bool = False,
    pyproject_content: Optional[str] = None
):
    """
    Runs a Unified Root sandbox test case.
    
    Args:
        sandbox_path: The root directory for this test (provided by fixture).
        test_name: Name of the test case.
        description: Description of what is being tested.
        input_config_content: Content of the app config (YAML/JSON).
        expected_output_desc: Description of expected outcome.
        validation_fn: Function to validate the resulting directory structure.
                       Receives (root_context, sandbox_path).
        use_rotation: Whether to enable log rotation in binder.
        pyproject_content: Optional content for pyproject.toml to mock project context.
    """
    print(f"\n--- Unified Root Test: {test_name} ---")
    print(f"Description: {description}")
    
    # 1. Setup Input Config
    config_file = sandbox_path / "app_config.json" # Use JSON by default for realism
    config_file.write_text(input_config_content, encoding="utf-8")
    
    if pyproject_content:
        (sandbox_path / "pyproject.toml").write_text(pyproject_content, encoding="utf-8")
    
    # 3. Execute Unified Root Creation
    # We MUST switch CWD to sandbox_path so relative paths in config are created inside sandbox
    # AND so that AppConfig defaults (like reading pyproject.toml) use the sandbox context.
    original_cwd = os.getcwd()
    binder = FileSystemBinder() 
    
    try:
        os.chdir(sandbox_path)
        print(f"Changed CWD to {sandbox_path}")
        
        # 2. Load Config (Moved inside CWD context)
        loader = FileConfigLoader()
        try:
            # We must use filename relative to CWD (which is now sandbox_path)
            # Or absolute path. config_file is likely absolute.
            app_config = loader.load(config_file, AppConfig)
        except Exception as e:
            pytest.fail(f"Setup failed: Could not load app config in sandbox: {e}")
            return

        # Bind! This creates the directories
        context = binder.bind(app_config)
        
        print(f"Unified Root created at: {context.root}")
        
    except Exception as e:
        print(f"Action Failed: {e}")
        # Allow validation to assert on failure if needed, or re-raise
        raise e
    finally:
        os.chdir(original_cwd)
        print("Restored CWD")

    # 4. Validation
    print(f"Expected: {expected_output_desc}")
    try:
        validation_fn(context, sandbox_path)
        print("✅ Validation Passed")
    except AssertionError as e:
        print(f"❌ Validation Failed: {e}")
        raise e
    except Exception as e:
        print(f"❌ Validation Error: {e}")
        raise e
