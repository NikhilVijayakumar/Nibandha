
import os
import json
import pytest
from pathlib import Path
from typing import Callable, Any, Dict, List
from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.configuration.infrastructure.file_loader import FileConfigLoader
from nibandha.unified_root.infrastructure.filesystem_binder import FileSystemBinder
from nibandha.export.application.export_service import ExportService
from tests.sandbox.core.runner import SandboxRunner, SandboxTestSpec, SandboxTestResult

def create_sandbox_env(sandbox_path: Path, config_dict: Dict[str, Any] = None) -> Dict[str, Path]:
    """
    Creates a standardized sandbox environment with input/output directories and app_config.json.
    
    Args:
        sandbox_path: The root of the sandbox.
        config_dict: Optional dictionary to merge into default AppConfig.
        
    Returns:
        Dict with 'input', 'output' paths.
    """
    input_dir = (sandbox_path / "input").resolve() # Force absolute
    input_dir.mkdir(parents=True, exist_ok=True)
    
    output_dir = (sandbox_path / "output").resolve() # Force absolute
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Default Config matching Happy Path structure
    full_config = {
        "name": "ExportSandBoxApp",
        "mode": "dev",
        "logging": {
            "level": "INFO",
            "enabled": True,
            "log_dir": str((sandbox_path / ".ExportRoot/logs").resolve()), # Absolute
            "rotation_enabled": False,
            "max_size_mb": 5.0,
            "rotation_interval_hours": 24,
            "archive_retention_days": 30,
            "backup_count": 10,
            "archive_dir": "logs/archive",
            "timestamp_format": "%Y-%m-%d"
        },
        "unified_root": {
            "name": ".ExportRoot",
            "custom_structure": {}
        },
        "reporting": {
            "output_dir": str((sandbox_path / ".ExportRoot/Report").resolve()), # Absolute
            "template_dir": "src/nikhil/nibandha/reporting/templates",
            "project_name": "ExportSandBoxApp",
            "quality_target": "src",
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
        "export": {
            "formats": ["html"],
            "style": "default",
            "input_dir": str(input_dir), # Absolute
            "template_dir": "src/nikhil/nibandha/export/infrastructure/templates",
            "styles_dir": "src/nikhil/nibandha/export/infrastructure/styles",
            "output_dir": str(output_dir), # Absolute
            "output_filename": "report",
            "export_order": None,
            "exclude_files": [],
            "metrics_mapping": {}
        }
    }
    
    if config_dict:
        # Deep merge simplistic
        for k, v in config_dict.items():
            if isinstance(v, dict) and k in full_config:
                full_config[k].update(v)
            else:
                full_config[k] = v
                
    (input_dir / "app_config.json").write_text(json.dumps(full_config, indent=2))
    
    return {"input": input_dir, "output": output_dir, "config_path": input_dir / "app_config.json"}

def run_export_test(
    sandbox_path: Path,
    test_name: str,
    description: str,
    export_config: Dict[str, Any],
    input_files: Dict[str, str],
    expected_files: List[str],
    validation_fn: Callable[[Any, Path], None] = None
):
    """
    Runs an Export module sandbox test.
    
    Args:
        sandbox_path: Sandbox root.
        test_name: Name of the test.
        description: Description of the test.
        export_config: Dictionary covering the 'export' section of AppConfig (and others if needed).
                       Defaults for logging/reporting/unified_root will be added if missing.
        input_files: Dictionary mapping filename -> content (markdown) to be placed in input_dir.
        expected_files: List of filenames expected in output_dir.
        validation_fn: Optional custom validation.
    """
    runner = SandboxRunner(sandbox_path)
    
    # 1. Prepare Configuration
    # Input artifacts (markdown) stay in `input/`
    # Output artifacts (html/docx) go to `output/`
    
    # We set input_dir to "../input" because we will execute from "output/"
    # OR we use absolute paths. SandboxRunner doesn't expose absolute input path easily in spec, 
    # but we know the structure.
    
    full_config = {
        "name": "ExportTestApp",
        "unified_root": {"name": ".ExportRoot"},
        "reporting": {"output_dir": ".ExportRoot/Report"},
        "export": {
            "formats": ["html"],
            "style": "default",
            "input_dir": "../input",  # Relative to output/
            "template_dir": "src/nikhil/nibandha/export/infrastructure/templates",
            "styles_dir": "src/nikhil/nibandha/export/infrastructure/styles",
            "output_dir": "Exports",  # Relative to output/
            "output_filename": "report",
            "export_order": None,
            "exclude_files": [],
            "metrics_mapping": {},
            **export_config 
        }
    }
    
    input_content = json.dumps(full_config, indent=2)
    
    expected_desc = f"Generate {len(expected_files)} files in output/Exports: {', '.join(expected_files)}"

    spec = SandboxTestSpec(
        name=test_name,
        description=description,
        input_filename="app_config.json",
        input_content=input_content,
        expected_output_desc=expected_desc
    )

    def action(input_file: Path) -> List[str]:
        # input_file is .../input/app_config.json
        input_dir = input_file.parent
        
        # 0. Setup Manual Inputs (Markdown files)
        # We perform this here to ensure it's part of the test "setup" phase effectively
        for fname, content in input_files.items():
            (input_dir / fname).write_text(content, encoding="utf-8")

        output_dir = sandbox_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # We execute inside output_dir
        original_cwd = os.getcwd()
        
        try:
            os.chdir(output_dir)
            
            # Load Config
            loader = FileConfigLoader()
            # input_file is absolute
            app_config = loader.load(input_file, AppConfig)
            
            # Bind (Creates .ExportRoot structure if needed, but we are using direct paths mostly)
            binder = FileSystemBinder()
            context = binder.bind(app_config)
                
            # Run Export
            service = ExportService(app_config.export)
            # Use unified export for integration tests (combining inputs)
            results = service.export_unified()
            
            return [str(p) for p in results]
            
        finally:
            os.chdir(original_cwd)

    def default_validation(results: List[str], output_root: Path):
        # output_root is sandbox_path/output
        # Config output_dir was "Exports" (relative)
        
        target_dir = output_root / "Exports"
        
        exported_files_found = []
        for exp in expected_files:
            if (target_dir / exp).exists():
                exported_files_found.append(exp)
        
        missing = set(expected_files) - set(exported_files_found)
        if missing:
             pytest.fail(f"Missing expected export artifacts in {target_dir}: {missing}")

        if validation_fn:
            validation_fn(results, output_root)

    result = runner.run_test(spec, action, default_validation)

    if result.result.startswith("FAIL"):
        pytest.fail(result.result)
