
from pathlib import Path
import json
import textwrap
from nibandha.unified_root.domain.models.root_context import RootContext
from nibandha.unified_root.domain.models.root_context import RootContext
from tests.sandbox.unified_root.utils import run_ur_test, BASE_CONFIG_TEMPLATE

def test_idempotency_strict(sandbox_root: Path):
    """
    Scenario: Directories already exist matching the strict config.
    Expectation: Binder succeeds, preserving files.
    """
    config_data = BASE_CONFIG_TEMPLATE.copy()
    config_data["name"] = "IdempotentApp"
    config_data["unified_root"]["name"] = ".IdempotentApp"
    config_data["logging"]["log_dir"] = ".IdempotentApp/logs"
    config_data["reporting"]["output_dir"] = ".IdempotentApp/Report"
    
    # Pre-create
    target_root = sandbox_root / ".IdempotentApp"
    (target_root / "logs").mkdir(parents=True)
    (target_root / "logs" / "marker.txt").write_text("should stay")
    
    def validation(context: RootContext, root_path: Path):
        assert (root_path / ".IdempotentApp" / "logs" / "marker.txt").read_text() == "should stay"

    run_ur_test(
        sandbox_path=sandbox_root,
        test_name="Corner - Idempotency Strict",
        description="Verify existing directories are respected with strict config.",
        input_config_content=json.dumps(config_data, indent=2),
        expected_output_desc="Success, marker preserved.",
        validation_fn=validation
    )

def test_project_fallback_strict(sandbox_root: Path):
    """
    Scenario: 'name' removed from JSON. 'unified_root.name' set to None.
    Expectation: AppConfig loads, resolves Project Name from mocked pyproject.toml,
                 AND sets unified_root.name and paths accordingly.
                 Binder receives full config and creates it.
    """
    config_data = BASE_CONFIG_TEMPLATE.copy()
    config_data.pop("name") # Trigger fallback
    config_data["unified_root"]["name"] = None # Trigger fallback
    # Note: explicit log_dir in Base Template is ".Nibandha/logs". 
    # If we want DYNAMIC resolution, we must set them to None so AppConfig resolves them.
    config_data["logging"]["log_dir"] = "logs" # "logs" triggers resolution
    config_data["reporting"]["output_dir"] = None # Trigger resolution
    
    pyproject_content = textwrap.dedent("""
    [project]
    name = "MockedProject"
    """)
    
    def validation(context: RootContext, root_path: Path):
        # AppConfig should have resolved name="MockedProject"
        # And unified_root=".MockedProject"
        expected_root = root_path / ".MockedProject"
        assert expected_root.exists()
        assert (expected_root / "logs").exists()

    run_ur_test(
        sandbox_path=sandbox_root,
        test_name="Corner - Project Fallback Strict",
        description="Verify AppConfig resolves defaults before Binder execution.",
        input_config_content=json.dumps(config_data, indent=2),
        expected_output_desc="Root '.MockedProject' created.",
        validation_fn=validation,
        pyproject_content=pyproject_content
    )
