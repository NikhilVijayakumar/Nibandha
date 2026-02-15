
import pytest
import os
from pathlib import Path
from typing import Callable
from nibandha.configuration.infrastructure.file_loader import FileConfigLoader
from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.unified_root.infrastructure.filesystem_binder import FileSystemBinder
from tests.sandbox.core.runner import SandboxRunner, SandboxTestSpec

# Helper: Run Single Config Test
def run_single_config_test(
    sandbox_path: Path,
    test_name: str,
    description: str,
    config_content: str,
    expected_output_desc: str,
    validation_fn: Callable[[Path], None]
):
    """
    Runs a unified root test with a single valid app_config.json.
    Uses SandboxRunner for standardized reporting.
    """
    runner = SandboxRunner(sandbox_path)
    
    spec = SandboxTestSpec(
        name=test_name,
        description=description,
        input_filename="app_config.json",
        input_content=config_content,
        expected_output_desc=expected_output_desc
    )

    def action(input_file: Path) -> str:
        original_cwd = os.getcwd()
        binder = FileSystemBinder()
        loader = FileConfigLoader()

        try:
            output_dir = sandbox_path / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            os.chdir(output_dir)
            
            # Load the single valid config
            app_config = loader.load(input_file, AppConfig)
            app_name = app_config.name
            
            print(f"Binding Component: {app_name}...")
            binder.bind(app_config)
            
            return app_name

        except Exception as e:
            raise e
        finally:
            os.chdir(original_cwd)

    def validation(result_data: str, root: Path):
        validation_fn(root)

    result = runner.run_test(spec, action, validation)

    if result.result.startswith("FAIL"):
        pytest.fail(result.result)


# --- Scenarios ---

def test_scenario_1_nibandha_standalone(sandbox_root: Path):
    """
    Scenario 1: Nibandha (Single App) with no custom structure.
    Root: .Nibandha
    """
    config_content = """{
  "name": "Nibandha",
  "mode": "production",
  "logging": {
    "level": "INFO",
    "enabled": true,
    "log_dir": ".Nibandha/logs",
    "rotation_enabled": false,
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
    "module_discovery": null
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
    "output_dir": ".Nibandha/Report",
    "output_filename": "report",
    "export_order": null,
    "exclude_files": [],
    "metrics_mapping": {}
  }
}"""
    
    def validation(root_path: Path):
        root = root_path / ".Nibandha"
        assert root.exists(), f".Nibandha root should exist"
        assert (root / "logs").exists(), f"logs should exist at root level"
        assert (root / "Report").exists(), f"Report should exist at root level"

    run_single_config_test(
        sandbox_path=sandbox_root,
        test_name="Ecosystem_1_Nibandha",
        description="Nibandha Standalone (Flat structure, no custom_structure).",
        config_content=config_content,
        expected_output_desc="Flat .Nibandha structure with logs, config, Report.",
        validation_fn=validation
    )

def test_scenario_2_pravaha_with_nibandha(sandbox_root: Path):
    """
    Scenario 2: Pravaha (Main App) with Nibandha lib defined in custom_structure.
    Root: .Pravaha
    """
    config_content = """{
  "name": "Pravaha",
  "mode": "production",
  "logging": {
    "level": "INFO",
    "enabled": true,
    "log_dir": ".Pravaha/logs",
    "rotation_enabled": false,
    "max_size_mb": 5.0,
    "rotation_interval_hours": 24,
    "archive_retention_days": 30,
    "backup_count": 10,
    "archive_dir": "logs/archive",
    "timestamp_format": "%Y-%m-%d"
  },
  "reporting": {
    "output_dir": ".Pravaha/Report",
    "template_dir": "src/nikhil/nibandha/reporting/templates",
    "project_name": "Pravaha",
    "quality_target": "src/nikhil",
    "package_roots": ["nibandha"],
    "unit_target": "tests/unit",
    "e2e_target": "tests/e2e",
    "doc_paths": {
      "functional": "docs/features",
      "technical": "docs/technical",
      "test": "docs/test"
    },
    "module_discovery": null
  },
  "unified_root": {
    "name": ".Pravaha",
    "custom_structure": {
      "Nibandha": {
        "logs": {},
        "Report": {}
      }
    }
  },
  "export": {
    "formats": ["md", "html"],
    "style": "default",
    "input_dir": ".Pravaha/Report/details",
    "template_dir": "src/nikhil/nibandha/export/infrastructure/templates",
    "styles_dir": "src/nikhil/nibandha/export/infrastructure/styles",
    "output_dir": ".Pravaha/Report",
    "output_filename": "report",
    "export_order": null,
    "exclude_files": [],
    "metrics_mapping": {}
  }
}"""
    
    def validation(root_path: Path):
        root = root_path / ".Pravaha"
        assert root.exists(), f".Pravaha root should exist"
        
        # Pravaha (Main) - Flat at root level
        assert (root / "logs").exists(), f"Pravaha logs should exist"
        assert (root / "Report").exists(), f"Pravaha Report should exist"
        
        # Nibandha (Library) - Defined in custom_structure
        assert (root / "Nibandha").exists(), f"Nibandha folder from custom_structure should exist"
        assert (root / "Nibandha" / "logs").exists(), f"Nibandha/logs should exist"
        assert (root / "Nibandha" / "Report").exists(), f"Nibandha/Report should exist"

    run_single_config_test(
        sandbox_path=sandbox_root,
        test_name="Ecosystem_2_Pravaha",
        description="Pravaha + Nibandha (via custom_structure). Shared Root .Pravaha.",
        config_content=config_content,
        expected_output_desc="Pravaha flat at root, Nibandha nested via custom_structure.",
        validation_fn=validation
    )

def test_scenario_3_amsha_with_nibandha(sandbox_root: Path):
    """
    Scenario 3: Amsha (Main App) with Nibandha defined in custom_structure.
    Root: .Amsha
    """
    config_content = """{
  "name": "Amsha",
  "mode": "production",
  "logging": {
    "level": "INFO",
    "enabled": true,
    "log_dir": ".Amsha/logs",
    "rotation_enabled": false,
    "max_size_mb": 5.0,
    "rotation_interval_hours": 24,
    "archive_retention_days": 30,
    "backup_count": 10,
    "archive_dir": "logs/archive",
    "timestamp_format": "%Y-%m-%d"
  },
  "reporting": {
    "output_dir": ".Amsha/Report",
    "template_dir": "src/nikhil/nibandha/reporting/templates",
    "project_name": "Amsha",
    "quality_target": "src/nikhil",
    "package_roots": ["nibandha"],
    "unit_target": "tests/unit",
    "e2e_target": "tests/e2e",
    "doc_paths": {
      "functional": "docs/features",
      "technical": "docs/technical",
      "test": "docs/test"
    },
    "module_discovery": null
  },
  "unified_root": {
    "name": ".Amsha",
    "custom_structure": {
      "Nibandha": {
        "logs": {},
        "Report": {}
      }
    }
  },
  "export": {
    "formats": ["md", "html"],
    "style": "default",
    "input_dir": ".Amsha/Report/details",
    "template_dir": "src/nikhil/nibandha/export/infrastructure/templates",
    "styles_dir": "src/nikhil/nibandha/export/infrastructure/styles",
    "output_dir": ".Amsha/Report",
    "output_filename": "report",
    "export_order": null,
    "exclude_files": [],
    "metrics_mapping": {}
  }
}"""
    
    def validation(root_path: Path):
        root = root_path / ".Amsha"
        assert root.exists(), f".Amsha root should exist"
        assert (root / "logs").exists(), f"Amsha logs should exist"
        assert (root / "Nibandha").exists(), f"Nibandha from custom_structure should exist"
        assert (root / "Nibandha" / "logs").exists(), f"Nibandha/logs should exist"

    run_single_config_test(
        sandbox_path=sandbox_root,
        test_name="Ecosystem_3_Amsha",
        description="Amsha + Nibandha (via custom_structure). Shared Root .Amsha.",
        config_content=config_content,
        expected_output_desc="Amsha flat, Nibandha nested via custom_structure.",
        validation_fn=validation
    )

def test_scenario_4_akashvani_ecosystem(sandbox_root: Path):
    """
    Scenario 4: Akashvani (Main) with Amsha, Pravaha, Nibandha in custom_structure.
    Root: .Akashvani
    """
    config_content = """{
  "name": "Akashvani",
  "mode": "production",
  "logging": {
    "level": "INFO",
    "enabled": true,
    "log_dir": ".Akashvani/logs",
    "rotation_enabled": false,
    "max_size_mb": 5.0,
    "rotation_interval_hours": 24,
    "archive_retention_days": 30,
    "backup_count": 10,
    "archive_dir": "logs/archive",
    "timestamp_format": "%Y-%m-%d"
  },
  "reporting": {
    "output_dir": ".Akashvani/Report",
    "template_dir": "src/nikhil/nibandha/reporting/templates",
    "project_name": "Akashvani",
    "quality_target": "src/nikhil",
    "package_roots": ["nibandha"],
    "unit_target": "tests/unit",
    "e2e_target": "tests/e2e",
    "doc_paths": {
      "functional": "docs/features",
      "technical": "docs/technical",
      "test": "docs/test"
    },
    "module_discovery": null
  },
  "unified_root": {
    "name": ".Akashvani",
    "custom_structure": {
      "Amsha": {
        "logs": {},
        "Report": {}
      },
      "Pravaha": {
        "logs": {},
        "Report": {}
      },
      "Nibandha": {
        "logs": {},
        "Report": {}
      }
    }
  },
  "export": {
    "formats": ["md", "html"],
    "style": "default",
    "input_dir": ".Akashvani/Report/details",
    "template_dir": "src/nikhil/nibandha/export/infrastructure/templates",
    "styles_dir": "src/nikhil/nibandha/export/infrastructure/styles",
    "output_dir": ".Akashvani/Report",
    "output_filename": "report",
    "export_order": null,
    "exclude_files": [],
    "metrics_mapping": {}
  }
}"""
    
    def validation(root_path: Path):
        root = root_path / ".Akashvani"
        assert root.exists(), f".Akashvani root should exist"
        
        # Akashvani (Main) - Flat
        assert (root / "logs").exists(), f"Akashvani logs should exist"
        
        # Libraries from custom_structure
        assert (root / "Amsha").exists(), f"Amsha from custom_structure should exist"
        assert (root / "Amsha" / "logs").exists(), f"Amsha/logs should exist"
        
        assert (root / "Pravaha").exists(), f"Pravaha from custom_structure should exist"
        assert (root / "Pravaha" / "logs").exists(), f"Pravaha/logs should exist"
        
        assert (root / "Nibandha").exists(), f"Nibandha from custom_structure should exist"
        assert (root / "Nibandha" / "logs").exists(), f"Nibandha/logs should exist"

    run_single_config_test(
        sandbox_path=sandbox_root,
        test_name="Ecosystem_4_Akashvani_Full",
        description="Akashvani + 3 Libs (via custom_structure). All sharing .Akashvani root.",
        config_content=config_content,
        expected_output_desc="Akashvani flat. Amsha/Pravaha/Nibandha nested via custom_structure.",
        validation_fn=validation
    )
