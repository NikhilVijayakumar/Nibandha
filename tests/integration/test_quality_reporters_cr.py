
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from src.nikhil.nibandha.reporting.quality.application.quality_reporter import QualityReporter

@pytest.fixture
def mock_dirs(tmp_path):
    return tmp_path / "output", tmp_path / "templates"

@pytest.fixture
def reporter(mock_dirs):
    output, templates = mock_dirs
    output.mkdir()
    templates.mkdir()
    # Create dummy templates
    (templates / "code_hygiene_report_template.md").write_text("Hygiene Report")
    (templates / "security_report_template.md").write_text("Security Report")
    (templates / "duplication_report_template.md").write_text("Duplication Report")
    (templates / "architecture_report_template.md").write_text("Arch")
    (templates / "type_safety_report_template.md").write_text("Type")
    (templates / "complexity_report_template.md").write_text("Complex")
    
    return QualityReporter(output, templates, source_root=Path("."))

@patch("src.nikhil.nibandha.reporting.quality.domain.hygiene_reporter.HygieneReporter.run")
@patch("src.nikhil.nibandha.reporting.quality.domain.security_reporter.SecurityReporter.run")
@patch("src.nikhil.nibandha.reporting.quality.domain.duplication_reporter.DuplicationReporter.run")
@patch("src.nikhil.nibandha.reporting.quality.application.quality_reporter.QualityReporter._run_architecture_check")
@patch("src.nikhil.nibandha.reporting.quality.application.quality_reporter.QualityReporter._run_type_check")
@patch("src.nikhil.nibandha.reporting.quality.application.quality_reporter.QualityReporter._run_complexity_check")
def test_quality_reporter_runs_new_checks(
    mock_complex, mock_type, mock_arch,
    mock_dup, mock_sec, mock_hyg,
    reporter
):
    # Setup mocks
    mock_hyg.return_value = {"status": "PASS", "violation_count": 0, "details": {}}
    mock_sec.return_value = {"status": "PASS", "violation_count": 0, "details": {}}
    mock_dup.return_value = {"status": "PASS", "violation_count": 0, "details": []}
    mock_arch.return_value = {"status": "PASS", "output": ""}
    mock_type.return_value = {"status": "PASS", "output": "", "violation_count": 0}
    mock_complex.return_value = {"status": "PASS", "output": "", "violation_count": 0}

    # Run
    results = reporter.run_checks()
    reporter.generate(results)

    # Verify Calls
    assert mock_hyg.called
    assert mock_sec.called
    assert mock_dup.called
    
    # Verify Files Created
    details_dir = reporter.details_dir
    assert (details_dir / "08_code_hygiene_report.md").exists()
    assert (details_dir / "09_duplication_report.md").exists()
    assert (details_dir / "10_security_report.md").exists()
