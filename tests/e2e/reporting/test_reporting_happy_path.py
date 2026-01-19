
import pytest
from pathlib import Path
from nibandha.reporting import ReportGenerator

@pytest.fixture
def reporting_output(tmp_path):
    """Fixture to provide a clean output directory."""
    out_dir = tmp_path / "e2e_reports_happy"
    out_dir.mkdir()
    return out_dir

def test_rpt_e2e_001_unified_report_generation(reporting_output):
    """RPT-E2E-001/002: Verify generate_all() runs and produces reports."""
    # We use a mock target or current repo to ensure it runs
    root = Path.cwd()
    
    # We need to make sure we don't fail if tools (mypy/ruff) find issues.
    # The generator should suppress tool failures and just report them as "FAIL" status.
    
    gen = ReportGenerator(
        output_dir=str(reporting_output),
        docs_dir=str(root / "docs" / "test")
    )
    
    # Generate
    try:
        gen.generate_all(
            unit_target="tests/unit/reporting", # Small target
            e2e_target="tests/unit/reporting", # Fake target for speed
            package_target="src/nikhil/nibandha/reporting", # Small target
            project_root="."
        )
    except Exception as e:
        pytest.fail(f"Generation failed with error: {e}")
    
    # Verify Directory Structure
    assert (reporting_output / "data").exists()
    assert (reporting_output / "assets").exists()
    
    # Verify Core Reports exist
    reports = [
        "unit_report.md",
        "e2e_report.md",
        "architecture_report.md", 
        "complexity_report.md", 
        "quality_overview.md",
        "module_dependency_report.md",
        "overview.md"
    ]
    
    for r in reports:
        if r == "overview.md":
            p = reporting_output / r
        else:
            p = reporting_output / "data" / r
        # We just want to ensure it created *something*, even if it says "No data"
        assert p.exists(), f"Report {r} not generated"
