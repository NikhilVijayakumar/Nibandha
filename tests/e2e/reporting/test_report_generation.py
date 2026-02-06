

import pytest
import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from nibandha.reporting import ReportGenerator

# Sample Data
UNIT_JSON = {
    "summary": {"passed": 10, "failed": 0, "skipped": 0, "error": 0},
    "tests": [
        {"nodeid": "tests/unit/test_a.py::test_one", "outcome": "passed", "call": {"duration": 0.01}},
        {"nodeid": "tests/unit/test_b.py::test_two", "outcome": "passed", "call": {"duration": 0.02}}
    ]
}

E2E_JSON = {
    "summary": {"passed": 5, "failed": 0, "skipped": 0, "error": 0},
    "tests": [
        {"nodeid": "tests/e2e/test_flow.py::test_full", "outcome": "passed", "call": {"duration": 1.5}}
    ]
}

COVERAGE_JSON = {
    "totals": {"percent_covered": 85.0},
    "files": {
        "src/nikhil/nibandha/module_a.py": {
            "summary": {"covered_lines": 85, "num_statements": 100}
        }
    }
}

@pytest.fixture
def reporting_env(tmp_path):
    """Sets up a temporary reporting environment."""
    out_dir = tmp_path / "report_out"
    out_dir.mkdir()
    
    # Pre-populate data dir as if tools ran (standard locations)
    # Note: ReportGenerator usually writes to output_dir/assets/data
    # But run_pytest takes a specific path. 
    # In our mock, we will ensure these files exist where the reporter looks for them.
    
    data_dir = out_dir / "assets" / "data"
    data_dir.mkdir(parents=True)
    
    # Write sample files
    (data_dir / "unit.json").write_text(json.dumps(UNIT_JSON), encoding='utf-8')
    (data_dir / "e2e.json").write_text(json.dumps(E2E_JSON), encoding='utf-8')
    
    # Coverage is often at project root or passed explicitly. 
    # Utils.load_json usually defaults to local path or relative.
    # In ReportGenerator.run_unit_Tests, it loads Path("coverage.json").
    # We should mock load_json or ensure coverage.json is in cwd. 
    # For safety in test, we'll patch load_json or write to cwd if possible, 
    # but writing to cwd is bad practice.
    # Better to patch utils.load_json to return our data when coverage.json is requested.
    
    return out_dir

def mock_run_command_success(cmd, cwd=None):
    """Mocks successful tool execution."""
    cmd_str = " ".join(cmd)
    if "mypy" in cmd_str:
        return "src/module.py:10: error: Incompatible types [assignment]", "", 1 # Generate 1 error to trigger chart
    if "ruff" in cmd_str:
        return "", "", 0  # No complexity violations
    if "lint-imports" in cmd_str:
        return "", "", 0  # No architecture violations
    return "", "", 0

def mock_run_command_fail(cmd, cwd=None):
    """Mocks failed tool execution."""
    cmd_str = " ".join(cmd)
    if "mypy" in cmd_str:
        return "file.py:1: error: Bad type", "", 1
    if "ruff" in cmd_str:
        return "file.py:1:9: C901 Function is too complex (15 > 10)", "", 1
    if "lint-imports" in cmd_str:
        return "Contract violated", "", 1
    return "", "Error", 1

def mock_run_command_crash(cmd, cwd=None):
    """Mocks tool crashing/not found."""
    return "", "Command not found", 127

@pytest.mark.skipif(sys.platform == "win32", reason="Causes system freeze on Windows - see GitHub issue #XXX")
@patch("nibandha.reporting.shared.infrastructure.utils.run_pytest")
@patch("nibandha.reporting.quality.application.quality_reporter.QualityReporter._run_command")
@patch("nibandha.reporting.shared.infrastructure.utils.load_json")
@patch("nibandha.reporting.dependencies.infrastructure.analysis.package_scanner.subprocess.run")
@patch("nibandha.reporting.dependencies.application.dependency_reporter.DependencyReporter.generate")
@patch("nibandha.reporting.quality.domain.hygiene_reporter.HygieneReporter.run")
@patch("nibandha.reporting.quality.domain.security_reporter.SecurityReporter.run")
@patch("nibandha.reporting.quality.domain.duplication_reporter.DuplicationReporter.run")
def test_unified_report_generation_RPT_E2E_001(
    mock_dup_run, mock_sec_run, mock_hyg_run, mock_dep_gen,
    mock_pkg_subprocess, mock_load, mock_run_cmd, mock_pytest, reporting_env
):
    """
    RPT-E2E-001: Unified Report Generation (Positive)
    RPT-E2E-002: Report Existence (Positive)
    RPT-E2E-003: Quality Reports (Positive)
    RPT-E2E-004: Visualization Assets (Positive)
    """
    # Setup Mocks
    mock_pytest.return_value = True
    mock_run_cmd.side_effect = mock_run_command_success
    
    # Mock file-scanning reporters to prevent Windows freeze
    mock_hyg_run.return_value = {"status": "PASS", "violation_count": 0, "details": {}}
    mock_sec_run.return_value = {"status": "PASS", "violation_count": 0, "details": {"high": [], "medium": []}}
    mock_dup_run.return_value = {"status": "PASS", "violation_count": 0, "details": []}
    mock_dep_gen.return_value = None  # DependencyReporter.generate returns None
    
    # Mock PackageScanner subprocess calls to prevent hanging on Windows
    mock_pkg_result = MagicMock()
    mock_pkg_result.returncode = 0
    mock_pkg_result.stdout = "[]"  # Empty JSON list
    mock_pkg_result.stderr = ""
    mock_pkg_subprocess.return_value = mock_pkg_result
    
    # Mock load_json to handle coverage.json and others
    def side_effect_load_json(path):
        p = str(path)
        if "coverage.json" in p:
            return COVERAGE_JSON
        if "unit.json" in p:
            return UNIT_JSON
        if "e2e.json" in p:
            return E2E_JSON
        # Fallback to actually reading if it exists (for other data)
        if Path(path).exists():
            with open(path) as f:
                return json.load(f)
        return {}

    mock_load.side_effect = side_effect_load_json

    # Execute
    gen = ReportGenerator(output_dir=str(reporting_env))
    gen.generate_all()

    # Verification RPT-E2E-002: Reports Exist
    details = reporting_env / "details"
    assert (details / "01_introduction.md").exists()
    assert (details / "03_unit_report.md").exists()
    assert (details / "04_e2e_report.md").exists()
    assert (details / "05_architecture_report.md").exists() # RPT-E2E-003
    assert (details / "06_type_safety_report.md").exists()
    assert (details / "07_complexity_report.md").exists()
    assert (details / "14_conclusion.md").exists()
    
    # Verification RPT-E2E-004: Assets
    images = reporting_env / "assets" / "images"
    assert (images / "quality" / "architecture_status.png").exists()
    assert (images / "quality" / "type_errors_by_module.png").exists()
    
    # Check Content Checks (Basic)
    unit_rep = (details / "03_unit_report.md").read_text(encoding='utf-8')
    assert "85.0%" in unit_rep # Coverage
    assert "Passed" in unit_rep
    assert "10" in unit_rep or "10 ✅" in unit_rep
    
    # NEW ASSERTION: Verify run_pytest args
    # We expect run_pytest to be called 2 times (unit, e2e)
    # Check the first call (unit tests) for coverage target
    assert mock_pytest.call_count >= 1
    args, _ = mock_pytest.call_args_list[0]
    # args: (target, json_path, cov_target)
    # Default behavior: cov_target should be "src/nikhil/nibandha" (or "src" depending on fallback resolution in test env)
    # In this test env, config is default. Default quality_target is "src".
    # Wait, in Generator, quality_target_default = "src".
    # So we expect "src".
    assert args[2] == "src"

@pytest.mark.skipif(sys.platform == "win32", reason="Causes system freeze on Windows - see GitHub issue #XXX")
@patch("nibandha.reporting.shared.infrastructure.utils.run_pytest")
@patch("nibandha.reporting.quality.application.quality_reporter.QualityReporter._run_command")
@patch("nibandha.reporting.shared.infrastructure.utils.load_json")
@patch("nibandha.reporting.dependencies.infrastructure.analysis.package_scanner.subprocess.run")
@patch("nibandha.reporting.dependencies.application.dependency_reporter.DependencyReporter.generate")
@patch("nibandha.reporting.quality.domain.hygiene_reporter.HygieneReporter.run")
@patch("nibandha.reporting.quality.domain.security_reporter.SecurityReporter.run")
@patch("nibandha.reporting.quality.domain.duplication_reporter.DuplicationReporter.run")
def test_missing_tool_output_RPT_E2E_007(
    mock_dup_run, mock_sec_run, mock_hyg_run, mock_dep_gen,
    mock_pkg_subprocess, mock_load, mock_run_cmd, mock_pytest, reporting_env
):
    """
    RPT-E2E-007: Missing Tool Output (Negative)
    Verify quality reporting when external tools fail.
    """
    mock_pytest.return_value = True
    mock_run_cmd.side_effect = mock_run_command_fail # items exist but report failure
    
    # Mock file-scanning reporters
    mock_hyg_run.return_value = {"status": "PASS", "violation_count": 0, "details": {}}
    mock_sec_run.return_value = {"status": "PASS", "violation_count": 0, "details": {"high": [], "medium": []}}
    mock_dup_run.return_value = {"status": "PASS", "violation_count": 0, "details": []}
    mock_dep_gen.return_value = None
    
    # Mock PackageScanner to prevent hanging
    mock_pkg_result = MagicMock()
    mock_pkg_result.returncode = 0
    mock_pkg_result.stdout = "[]"
    mock_pkg_subprocess.return_value = mock_pkg_result
    
    # Use empty data for coverage to simulate missing coverage
    mock_load.side_effect = lambda p: {} 

    gen = ReportGenerator(output_dir=str(reporting_env))
    gen.generate_all()
    
    details = reporting_env / "details"
    
    # Architecture should show fail
    arch_rep = (details / "05_architecture_report.md").read_text(encoding='utf-8')
    assert "FAIL" in arch_rep or "Contract violated" in arch_rep
    
    # Type Safety should show fail
    type_rep = (details / "06_type_safety_report.md").read_text(encoding='utf-8')
    assert "fail" in type_rep.lower() or "error" in type_rep.lower()

@pytest.mark.skipif(sys.platform == "win32", reason="Causes system freeze on Windows - see GitHub issue #XXX")
@patch("nibandha.reporting.shared.infrastructure.utils.run_pytest")
@patch("nibandha.reporting.quality.application.quality_reporter.QualityReporter._run_command")
@patch("nibandha.reporting.shared.infrastructure.utils.load_json")
@patch("nibandha.reporting.dependencies.infrastructure.analysis.package_scanner.subprocess.run")
@patch("nibandha.reporting.dependencies.application.dependency_reporter.DependencyReporter.generate")
@patch("nibandha.reporting.quality.domain.hygiene_reporter.HygieneReporter.run")
@patch("nibandha.reporting.quality.domain.security_reporter.SecurityReporter.run")
@patch("nibandha.reporting.quality.domain.duplication_reporter.DuplicationReporter.run")
def test_tool_crash_handling(
    mock_dup_run, mock_sec_run, mock_hyg_run, mock_dep_gen,
    mock_pkg_subprocess, mock_load, mock_run_cmd, mock_pytest, reporting_env
):
    """
    Variant of RPT-E2E-007 where tools crash (exit 127 or similar).
    """
    mock_pytest.return_value = True
    mock_run_cmd.side_effect = mock_run_command_crash
    mock_load.return_value = {}
    
    # Mock file-scanning reporters
    mock_hyg_run.return_value = {"status": "PASS", "violation_count": 0, "details": {}}
    mock_sec_run.return_value = {"status": "PASS", "violation_count": 0, "details": {"high": [], "medium": []}}
    mock_dup_run.return_value = {"status": "PASS", "violation_count": 0, "details": []}
    mock_dep_gen.return_value = None
    
    # Mock PackageScanner to prevent hanging
    mock_pkg_result = MagicMock()
    mock_pkg_result.returncode = 0
    mock_pkg_result.stdout = "[]"
    mock_pkg_subprocess.return_value = mock_pkg_result

    gen = ReportGenerator(output_dir=str(reporting_env))
    gen.generate_all()
    
    details = reporting_env / "details"
    
    arch_rep = (details / "05_architecture_report.md").read_text(encoding='utf-8')
    assert "FAIL" in arch_rep # Should handle crash as fail
