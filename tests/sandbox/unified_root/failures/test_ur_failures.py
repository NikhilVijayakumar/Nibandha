
import pytest
import sys
import json
from pathlib import Path
from nibandha.unified_root.domain.models.root_context import RootContext
from nibandha.unified_root.domain.models.root_context import RootContext
from tests.sandbox.unified_root.utils import run_ur_test, BASE_CONFIG_TEMPLATE

@pytest.mark.skipif(sys.platform != "win32", reason="Invalid path characters are Windows-specific")
def test_invalid_chars_windows_strict(sandbox_root: Path):
    """
    Scenario: App Name contains invalid characters, causing creation failure.
    Uses strict full config.
    """
    config_data = BASE_CONFIG_TEMPLATE.copy()
    config_data["name"] = "Invalid:Name"
    
    def validation(context: RootContext, root_path: Path):
        pytest.fail("Should have raised exception")

    with pytest.raises(OSError):
        run_ur_test(
            sandbox_path=sandbox_root,
            test_name="Failure - Invalid Chars Strict",
            description="Verify failure when creating directory with invalid characters in Strict Config.",
            input_config_content=json.dumps(config_data, indent=2),
            expected_output_desc="OSError raised due to invalid path.",
            validation_fn=validation 
        )
