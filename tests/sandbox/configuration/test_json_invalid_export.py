
import pytest
from nibandha.configuration.domain.models.app_config import AppConfig
from tests.sandbox.configuration.utils import run_config_test
import json

def test_json_invalid_formats(sandbox_root):
    """
    Scenario: 'formats' contains unsupported values (e.g., 'bmp')
    Expected: ValidationError raised during loading.
    """
    config_data = {
        "name": "BadFormatApp",
        "export": {
            "formats": ["md", "bmp"] # 'bmp' is invalid
        }
    }

    # We expect a value error about unsupported format
    
    def action(p):
        AppConfig.model_validate_json(p.read_text())

    # We need to catch the error in the runner or here. 
    # run_config_test in utils.py fails if exception is raised in action unless we modify it?
    # The current utils.py simple wrapper doesn't support "expect failure".
    # Let's use pytest.raises around the validated call, and return "SUCCESS" if it raises?
    # Or just write the test logic directly.

    from tests.sandbox.core.runner import SandboxRunner, SandboxTestSpec
    
    runner = SandboxRunner(sandbox_root)
    spec = SandboxTestSpec(
        name="InvalidFormatsTest",
        description="Check validation for invalid export formats",
        input_filename="app_config.json",
        input_content=json.dumps(config_data),
        expected_output_desc="ValidationError"
    )

    def test_action(input_file):
        try:
            AppConfig.model_validate_json(input_file.read_text())
        except ValueError as e:
            if "Unsupported format" in str(e):
                return "Caught Expected Error"
            raise e
        return "Did not catch error"

    def validation(result, root):
        assert result == "Caught Expected Error"

    result = runner.run_test(spec, test_action, validation)
    if result.result.startswith("FAIL"):
        pytest.fail(result.result)

def test_json_docx_without_html(sandbox_root):
    """
    Scenario: 'formats' has 'docx' but not 'html'
    Expected: ValidationError (dependency missing)
    """
    config_data = {
        "name": "DocxNoHtmlApp",
        "export": {
            "formats": ["docx"] # missing html
        }
    }

    from tests.sandbox.core.runner import SandboxRunner, SandboxTestSpec
    runner = SandboxRunner(sandbox_root)
    spec = SandboxTestSpec(
        name="DocxDependencyTest",
        description="Check validation for docx without html",
        input_filename="app_config.json",
        input_content=json.dumps(config_data),
        expected_output_desc="ValidationError"
    )

    def test_action(input_file):
        try:
            AppConfig.model_validate_json(input_file.read_text())
        except ValueError as e:
             if "requires 'html'" in str(e):
                 return "Caught Expected Error"
             raise e
        return "Did not catch error"

    def validation(result, root):
        assert result == "Caught Expected Error"

    result = runner.run_test(spec, test_action, validation)
    if result.result.startswith("FAIL"):
        pytest.fail(result.result)
