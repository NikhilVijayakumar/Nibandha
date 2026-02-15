
import json
import datetime
import traceback
from pathlib import Path
from typing import Any, Callable, Optional, Dict
from pydantic import BaseModel, Field

class SandboxTestSpec(BaseModel):
    """Defines the input specification for a sandbox test."""
    name: str
    description: str
    input_filename: str
    input_content: str
    expected_output_desc: str
    should_fail: bool = False

class SandboxTestResult(BaseModel):
    """Captures the outcome of a sandbox test."""
    result: str = "PASS" # PASS or FAIL
    actual_output_desc: str = ""
    actual_output_data: Any = None
    error_log: Optional[str] = None

class SandboxRunner:
    """
    Orchestrates the execution of a sandbox test.
    Standardizes Setup -> Action -> Validation -> Reporting.
    """
    def __init__(self, sandbox_root: Path):
        self.sandbox_root = sandbox_root
        self.template_path = Path(__file__).parent / "templates" / "report_template.md"

    def run_test(
        self,
        spec: SandboxTestSpec,
        action: Callable[[Path], Any],
        validation: Callable[[Any, Path], None]
    ) -> SandboxTestResult:
        
        # 1. Setup
        input_file = self._setup_input(spec)
        result = SandboxTestResult()

        try:
            # 1.1 Setup Output Dir
            output_dir = self.sandbox_root / "output"
            output_dir.mkdir(parents=True, exist_ok=True)

            # 2. Action
            # Action returns some data (AppConfig object, or just a success flag, etc.)
            action_output = action(input_file)
            result.actual_output_data = action_output
            
            # 2.1 Auto-save Output
            self._save_output(action_output)

            # 3. Validation
            # Validation function asserts on the output OR the filesystem state
            # passed root is now the OUTPUT directory
            validation(action_output, output_dir)
            
            # If we got here, it passed execution and validation
            if spec.should_fail:
                result.result = "FAIL: Expected failure didn't occur."
                result.actual_output_desc = "Action/Validation succeeded, but expected failure."
            else:
                result.result = "PASS"
                result.actual_output_desc = "Validation Passed. Output matches expectations."

        except Exception as e:
            # 4. Failure Handling
            if spec.should_fail:
                # Needed failure occurred
                result.result = "PASS (Expected Failure)"
                result.error_log = traceback.format_exc()
                result.actual_output_desc = "Test failed as expected."
            else:
                result.result = f"FAIL: {str(e)}"
                result.error_log = traceback.format_exc()
                result.actual_output_desc = "Test Execution Failed."

        # 5. Reporting
        self._generate_report(spec, result)

        return result

    def _setup_input(self, spec: SandboxTestSpec) -> Path:
        input_dir = self.sandbox_root / "input"
        input_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = input_dir / spec.input_filename
        file_path.write_text(spec.input_content, encoding="utf-8")
        return file_path

    def _save_output(self, data: Any):
        output_dir = self.sandbox_root / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Only save if data is substantive (not None)
        if data is None:
            return

        try:
            if hasattr(data, "model_dump_json"):
                content = data.model_dump_json(indent=2)
            else:
                content = json.dumps(data, indent=2, default=str)
            
            (output_dir / "result.json").write_text(content, encoding="utf-8")
        except Exception:
            # If we can't serialize, we just ignore saving the file
            pass

    def _generate_report(self, spec: SandboxTestSpec, result: SandboxTestResult):
        if not self.template_path.exists():
            print(f"Warning: Template not found at {self.template_path}")
            return

        template = self.template_path.read_text(encoding="utf-8")
        
        # Determine format for syntax highlighting
        fmt = "text"
        if spec.input_filename.endswith(".json"): fmt = "json"
        elif spec.input_filename.endswith((".yaml", ".yml")): fmt = "yaml"
        elif spec.input_filename.endswith(".py"): fmt = "python"

        # Format output data safely
        try:
            if hasattr(result.actual_output_data, "model_dump_json"):
                output_json = result.actual_output_data.model_dump_json(indent=2)
            else:
                output_json = json.dumps(result.actual_output_data, indent=2, default=str)
        except:
            output_json = str(result.actual_output_data)

        # Basic Jinja-like replacement (keeping it simple without jinja2 dependency for now, or could use it if available)
        # Using string replace for zero-dependency standard lib approach
        content = template.replace("{{ test_name }}", spec.name)
        content = content.replace("{{ timestamp }}", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        content = content.replace("{{ result }}", result.result)
        content = content.replace("{{ description }}", spec.description)
        content = content.replace("{{ input_filename }}", spec.input_filename)
        content = content.replace("{{ input_format }}", fmt)
        content = content.replace("{{ input_content }}", spec.input_content)
        content = content.replace("{{ expected_output_desc }}", spec.expected_output_desc)
        content = content.replace("{{ actual_output_desc }}", result.actual_output_desc)
        content = content.replace("{{ actual_output_json }}", output_json)
        
        if result.error_log:
            # Handle conditional block roughly (remove if no error)
            # Since we are doing manual replace, we just append errors if present
            # The template has {% if error_log %}, we can't parse that with replace.
            # Let's just hard replace the block marker.
            pass 
        
        # Manual template logic for the optional error block
        error_section = ""
        if result.error_log:
            error_section = f"\n## Errors\n```text\n{result.error_log}\n```\n"
        
        # Remove jinja tags from template if we use simple replace, or regex sub
        # For simplicity, let's just assume the template uses {{ }} and we replace them.
        # For the if block, we will just simulate it.
        
        # Clean up the Jinja markers from the template string first if we aren't using Jinja
        # Actually, let's just use string replacement for the vars we know.
        # And regex to remove the {% %} blocks?
        
        # Simpler: Just reconstruct the content string here if template is simple, 
        # OR use the template but strict replacement.
        
        # Let's fix the template handling. 
        # We will replace `{% if error_log %}` ... `{% endif %}` with the error content or empty string.
        
        import re
        error_pattern = re.compile(r"{% if error_log %}(.*?){% endif %}", re.DOTALL)
        
        def error_replacer(match):
            if result.error_log:
                return match.group(1).replace("{{ error_log }}", result.error_log)
            return ""

        content = error_pattern.sub(error_replacer, content)

        report_path = self.sandbox_root / "report.md"
        report_path.write_text(content, encoding="utf-8")

