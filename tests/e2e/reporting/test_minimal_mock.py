"""Simple test to verify mock strategy prevents Windows freeze."""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

@patch("nibandha.reporting.shared.infrastructure.utils.run_pytest")
@patch("nibandha.reporting.quality.application.quality_reporter.QualityReporter.run_checks")
@patch("nibandha.reporting.dependencies.application.dependency_reporter.DependencyReporter.generate")
def test_minimal_generate_all(mock_dep, mock_qual, mock_pytest, tmp_path):
    """Minimal test with aggressive mocking to avoid freezes."""
    # Mock pytest
    mock_pytest.return_value = True
    
    # Mock quality checks to return minimal data
    mock_qual.return_value = {
        "architecture": {"status": "PASS", "output": ""},
        "type_safety": {"status": "PASS", "output": "", "violation_count": 0},
        "complexity": {"status": "PASS", "output": "", "violation_count": 0},
        "hygiene": {"status": "PASS", "violation_count": 0, "details": {}},
        "security": {"status": "PASS", "violation_count": 0, "details": {"high": [], "medium": []}},
        "duplication": {"status": "PASS", "violation_count": 0, "details": []}
    }
    
    # Mock dependency reporter
    mock_dep.return_value = None
    
    # Import after mocks are set
    from nibandha.reporting import ReportGenerator
    
    # Create generator
    gen = ReportGenerator(output_dir=str(tmp_path))
    
    # This should not freeze
    gen.generate_all()
    
    # Basic validation
    assert (tmp_path / "details").exists()
    print("✓ Test completed without freezing!")

if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        test_minimal_generate_all(Path(td))
