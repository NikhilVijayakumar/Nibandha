
import json
import datetime
import traceback
from pathlib import Path
from typing import Any, Callable, Dict, Optional

def setup_test_case(sandbox_root: Path, input_content: str, filename: str) -> Path:
    """
    Sets up the test case by creating the input directory and writing the input file.
    Returns the path to the created input file.
    """
    input_dir = sandbox_root / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    
    input_file = input_dir / filename
    input_file.write_text(input_content, encoding="utf-8")
    
    return input_file

def dump_result(sandbox_root: Path, data: Any, filename: str = "result.json"):
    """
    Dumps the result data to the output directory.
    """
    output_dir = sandbox_root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / filename
    
    if isinstance(data, str):
        output_file.write_text(data, encoding="utf-8")
    else:
        # Assume dict/list or Pydantic model
        if hasattr(data, "model_dump"):
            json_content = data.model_dump_json(indent=4)
        else:
            json_content = json.dumps(data, indent=4, default=str)
        output_file.write_text(json_content, encoding="utf-8")

def generate_config_report(
    sandbox_path: Path, 
    test_name: str, 
    description: str, 
    input_filename: str,
    input_content: str,
    expected_output: str,
    actual_output: Any,
    result: str = "PASS"
):
    """
    Generates a Markdown report for the configuration test execution.
    """
    # Template stored in same directory as utils.py for simplicity in sandbox
    template_path = Path(__file__).parent / "templates" / "config_report_template.md"
    
    if not template_path.exists():
        # Fallback to simple string if template is missing
        print(f"Warning: Template not found at {template_path}. Using simple fallback.")
        template_content = "# Configuration Test Report: {{ test_name }}\n\n**Result**: {{ result }}\n\n**Description**: {{ description }}\n\n## Input\n\n```{{ input_format }}\n{{ input_content }}\n```\n\n## Output\n\n**Expected**: {{ expected_output }}\n\n**Actual**:\n\n```json\n{{ actual_output }}\n```"
    else:
        template_content = template_path.read_text(encoding="utf-8")

    # Determine input format for code block
    if input_filename.endswith((".yaml", ".yml")):
        input_format = "yaml"
    elif input_filename.endswith(".json"):
        input_format = "json"
    elif input_filename.endswith(".py"):
        input_format = "python"
    else:
        input_format = "text"

    # Format actual output
    if isinstance(actual_output, str):
        formatted_actual = actual_output
    elif hasattr(actual_output, "model_dump_json"):
        formatted_actual = actual_output.model_dump_json(indent=4)
    else:
        formatted_actual = json.dumps(actual_output, indent=4, default=str)

    content = template_content.replace("{{ test_name }}", test_name)
    content = content.replace("{{ timestamp }}", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    content = content.replace("{{ result }}", result)
    content = content.replace("{{ description }}", description)
    content = content.replace("{{ input_filename }}", input_filename)
    content = content.replace("{{ input_format }}", input_format)
    content = content.replace("{{ input_content }}", input_content)
    content = content.replace("{{ expected_output }}", expected_output)
    content = content.replace("{{ actual_output }}", formatted_actual)
    
    report_path = sandbox_path / "report.md"
    report_path.write_text(content, encoding="utf-8")
    print(f"Generated report at {report_path}")

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
    Orchestrates the test execution: setup, action, validation, result dumping, and reporting.
    """
    # 1. Setup
    input_file = setup_test_case(sandbox_path, input_content, input_filename)
    
    actual_result = None
    result_status = "PASS"
    
    try:
        # 2. Action
        actual_result = action(input_file)
        
        # 3. Validation
        validation(actual_result)
        
        # 4. Dump Success Result
        dump_result(sandbox_path, actual_result, "loaded_config.json")
        
    except Exception as e:
        # Handle Failure
        result_status = f"FAIL: {str(e)}"
        actual_result = f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        dump_result(sandbox_path, actual_result, "error.txt")
        # Don't re-raise yet, we want to generate report first
        
    # 5. Report
    generate_config_report(
        sandbox_path,
        test_name,
        description,
        input_filename,
        input_content,
        expected_output_desc,
        actual_result,
        result_status
    )
    
    # 6. Re-raise if failed to fail the pytest test
    if result_status.startswith("FAIL"):
        if isinstance(actual_result, str) and "Traceback" in actual_result:
             # If we caught an exception, we want pytest to know about it, 
             # but we already captured it. We can raise a generic assertion error with the message.
             pytest.fail(result_status)
        else:
             pytest.fail(result_status)

import pytest # Needed for fail
