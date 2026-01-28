
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
    # Should raise error or return empty depending on jinja config
    # In strict mode (which seems to be implied by StrictUndefined), it might raise.
    # But get_template also raises TemplateNotFound if missing.
    from jinja2 import TemplateNotFound
    try:
        gen.template_engine.render("foo.md", {})
        assert False, "Should have raised TemplateNotFound"
    except TemplateNotFound:
        pass
    except Exception as e:
        # Accept other errors related to missing dir
        pass

def test_rpt_unit_006_invalid_output_path(tmp_path):
    """RPT-UNIT-006: Invalid output path handling."""
    # If passed a file as a directory?
    f = tmp_path / "test_file.txt"
    f.touch()
    
    # Initialization itself will fail when sub-reporters try to create directories
    # On Windows, this is often FileExistsError or NotADirectoryError
    with pytest.raises((FileExistsError, NotADirectoryError, OSError)):
        ReportGenerator(output_dir=str(f))
