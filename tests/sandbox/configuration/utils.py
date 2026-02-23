
import pytest
from pathlib import Path
from typing import Any, Callable
from tests.sandbox.core.runner import SandboxRunner, SandboxTestSpec

def run_config_test(
    sandbox_path: Path,
    test_name: str,
    description: str,
    input_filename: str,
    input_content: str,
    expected_output_desc: str,
    action: Callable[[Path], Any],
    validation: Callable[[Any], None]
):
    """
    Orchestrates the test execution using the standardized SandboxRunner.
    Adapts the old signature to the new runner.
    """
    runner = SandboxRunner(sandbox_path)
    
    spec = SandboxTestSpec(
        name=test_name,
        description=description,
        input_filename=input_filename,
        input_content=input_content,
        expected_output_desc=expected_output_desc
    )

    # Adapt validation signature: 
    # New runner expects validation(output, sandbox_root)
    # Old validation was validation(output)
    def typesafe_validation(output: Any, root: Path):
        validation(output)

    result = runner.run_test(spec, action, typesafe_validation)

    if result.result.startswith("FAIL"):
        pytest.fail(result.result)

