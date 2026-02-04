import pytest
from unittest.mock import MagicMock, patch
from nikhil.nibandha.reporting.quality.application.quality_reporter import QualityReporter
from pathlib import Path

class TestQualityReporterFix:
    def test_run_type_check_passes_on_zero_violations_with_error_code(self):
        """
        Verify that _run_type_check returns PASS if violation count is 0,
        even if the subprocess returns a non-zero exit code (e.g. config warnings).
        """
        reporter = QualityReporter(
            output_dir=Path("tmp"),
            templates_dir=Path("tmp")
        )
        
        # Mock _run_command to simulate exit code 1 but 0 "error:" in output
        # Mypy output often contains headers/footers.
        mock_output = "Success: no issues found in 1 source file\n" 
        # Note: If exit code is 1, usually there is an error, but sometimes it's configuration related.
        # The key requirement is: if "error:" count is 0, we treat it as PASS.
        
        with patch.object(reporter, '_run_command', return_value=(mock_output, "", 1)) as mock_cmd:
            with patch.object(reporter, '_get_executable', return_value="mypy"):
                result = reporter._run_type_check("some_target")
                
                assert result["status"] == "PASS"
                assert result["violation_count"] == 0

    def test_run_complexity_check_passes_on_zero_violations_with_error_code(self):
        """
        Verify that _run_complexity_check returns PASS if violation count is 0,
        even if the subprocess returns a non-zero exit code.
        """
        reporter = QualityReporter(
            output_dir=Path("tmp"),
            templates_dir=Path("tmp")
        )
        
        # Mock output with no C901 codes
        mock_output = "Some other ruff output\n"
        
        with patch.object(reporter, '_run_command', return_value=(mock_output, "", 1)) as mock_cmd:
             with patch.object(reporter, '_get_executable', return_value="ruff"):
                result = reporter._run_complexity_check("some_target")
                
                assert result["status"] == "PASS"
                assert result["violation_count"] == 0
