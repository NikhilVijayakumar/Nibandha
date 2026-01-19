
import pytest
from pathlib import Path
from nibandha.reporting import ReportGenerator


def test_rpt_unit_002_custom_templates(tmp_path):
    """RPT-UNIT-002: Verify custom template directory."""
    tmpl_dir = tmp_path / "custom_templates"
    tmpl_dir.mkdir()
    
    gen = ReportGenerator(output_dir=str(tmp_path), template_dir=str(tmpl_dir))
    assert gen.templates_dir == tmpl_dir.resolve()
    assert gen.unit_reporter.templates_dir == tmpl_dir.resolve()

def test_rpt_unit_004_path_resolution(tmp_path):
    """RPT-UNIT-004: Verify relative path resolution."""
    import os
    orig_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        gen = ReportGenerator(output_dir="./rel_out")
        expected = (tmp_path / "rel_out").resolve()
        assert gen.output_dir == expected
    finally:
        os.chdir(orig_cwd)
