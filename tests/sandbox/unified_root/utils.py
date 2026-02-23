
import os
import shutil
import pytest
from pathlib import Path
from typing import Callable, Optional, Any
from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.configuration.infrastructure.file_loader import FileConfigLoader
from nibandha.unified_root.infrastructure.filesystem_binder import FileSystemBinder
from nibandha.unified_root.domain.models.root_context import RootContext
from tests.sandbox.core.runner import SandboxRunner, SandboxTestSpec, SandboxTestResult

# Base Template provided by User
BASE_CONFIG_TEMPLATE = {
    "name": "Nibandha",
    "mode": "production",
    "logging": {
        "level": "INFO",
        "enabled": True,
        "log_dir": ".Nibandha/logs",
        "rotation_enabled": False,
        "max_size_mb": 5.0,
        "rotation_interval_hours": 24,
        "archive_retention_days": 30,
        "backup_count": 10,
        "archive_dir": "logs/archive",
        "timestamp_format": "%Y-%m-%d"
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
        "export_order": None,
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
    pyproject_content: Optional[str] = None,
    expect_error: bool = False
):
    """
    Runs a Unified Root sandbox test case using SandboxRunner.
    """
    runner = SandboxRunner(sandbox_path)
    
    spec = SandboxTestSpec(
        name=test_name,
        description=description,
        input_filename="app_config.json",
        input_content=input_config_content,
        expected_output_desc=expected_output_desc,
        should_fail=expect_error
    )

    def action(input_file: Path) -> RootContext:
        output_dir = sandbox_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True) # Ensure it exists

        # 1. Additional Setup (pyproject.toml)
        if pyproject_content:
            (output_dir / "pyproject.toml").write_text(pyproject_content, encoding="utf-8")

        # 2. Execute within Sandbox Context
        original_cwd = os.getcwd()
        binder = FileSystemBinder()
        
        try:
            os.chdir(output_dir)
            # Load config from the input file (which SandboxRunner created)
            loader = FileConfigLoader()
            # input_file is absolute, so load it directly
            # BUT we need to ensure app execution uses the CWD for potential relative paths in logic
            app_config = loader.load(input_file, AppConfig)
            
            # Bind!
            context = binder.bind(app_config)
            return context
            
        except Exception as e:
            raise e
        finally:
            os.chdir(original_cwd)

    def validation(context: Any, root: Path):
        # Adapt signature
        if isinstance(context, RootContext):
            validation_fn(context, root)
        elif not expect_error:
            # If we didn't expect errors, context should be valid
            raise ValueError(f"Expected RootContext, got {type(context)}")
        # If expect_error is True, and Action succeeded (and returned context), 
        # SandboxRunner calls validation. 
        # Then SandboxRunner checks spec.should_fail.
        # If should_fail is True, it marks as FAIL "Expected failure didn't occur".
        # So validation logic allows us to verify the "Success" state if needed, 
        # but here we just pass through.
        pass

    result = runner.run_test(spec, action, validation)

    if result.result.startswith("FAIL"):
        pytest.fail(result.result)
