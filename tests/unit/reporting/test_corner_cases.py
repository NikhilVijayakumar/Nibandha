
import pytest
from pathlib import Path
from nibandha.reporting import ReportGenerator

def test_rpt_unit_005_missing_template_directory(tmp_path):
    """RPT-UNIT-005: Missing template dir should maybe fallback or error depending on design."""
    # Current design: It accepts the path as is, but reporters might fail later if they can't find files.
    # Or strict check in init?
    # Let's verify it simply accepts it (design choice) or check if we want it to fail.
    # Looking at core.py code: self.templates_dir = Path(template_dir).resolve()
    # It doesn't raise error if missing.
    
    missing_dir = tmp_path / "does_not_exist"
    gen = ReportGenerator(output_dir=str(tmp_path), template_dir=str(missing_dir))
    assert gen.templates_dir == missing_dir.resolve()
    assert not gen.templates_dir.exists()
    
    # Verify reporter behavior when template is missing
    # Reporter simply returns "Template not found" string in current impl
    res = gen.dep_reporter._load_template("foo.md")
    assert "Template not found" in res

def test_rpt_unit_006_invalid_output_path(tmp_path):
    """RPT-UNIT-006: Invalid output path handling."""
    # If passed a file as a directory?
    f = tmp_path / "test_file.txt"
    f.touch()
    
    # Initialization itself will fail when sub-reporters try to create directories
    # On Windows, this is often FileExistsError or NotADirectoryError
    with pytest.raises((FileExistsError, NotADirectoryError, OSError)):
        ReportGenerator(output_dir=str(f))
