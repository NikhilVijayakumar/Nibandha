
import pytest
from unittest.mock import MagicMock, patch, ANY
from pathlib import Path
import logging

from nibandha.export.application.export_service import ExportService
from nibandha.export.infrastructure.docx_exporter import DOCXExporter
from nibandha.export.infrastructure.html_tab_exporter import TabBasedHTMLExporter

# --- DOCX Exporter Robustness ---

def test_docx_missing_dependency(tmp_path):
    # Mock import failure using dict exclusion? Hard for 'import pypandoc'.
    # Easier to mock _check_dependencies or the flag.
    
    with patch("nibandha.export.infrastructure.docx_exporter.logger") as mock_logger:
        # Create instance with mocked dependency check hook if possible, or patch sys.modules
        # We'll just manually set the flag after init to verify export check
        exporter = DOCXExporter()
        exporter.pypandoc_available = False # Simulate missing
        
        res = exporter.export(tmp_path / "src.html", tmp_path / "out.docx")
        assert res is None
        mock_logger.error.assert_called_with(ANY)

def test_docx_source_missing(tmp_path):
    exporter = DOCXExporter()
    exporter.pypandoc_available = True
    
    res = exporter.export(tmp_path / "missing.html", tmp_path / "out.docx")
    assert res is None

def test_docx_conversion_error(tmp_path):
    exporter = DOCXExporter()
    exporter.pypandoc_available = True
    exporter.pypandoc = MagicMock()
    exporter.pypandoc.convert_file.side_effect = Exception("Pandoc crashed")
    
    src = tmp_path / "src.html"
    src.touch()
    
    res = exporter.export(src, tmp_path / "out.docx")
    assert res is None

# --- Export Service Robustness ---

@pytest.fixture
def service():
    return ExportService()

def test_export_service_missing_html_fail(service, tmp_path):
    # If HTML export fails, DOCX should abort
    src = tmp_path / "report.md"
    src.write_text("content")
    
    service.html_exporter.export = MagicMock(return_value=None) # Fail
    
    res = service.export_document(src, formats=["html", "docx"])
    
    # HTML fail -> return what we have (empty list)
    assert res == []
    # Verify DOCX not attempted
    # (impl detail: if html_path is None, docx logic normally skipped or logs error)

def test_export_service_intermediate_missing(service, tmp_path):
    # HTML succeeds returning path, but file somehow deleted before DOCX?
    src = tmp_path / "report.md"
    src.write_text("content")
    
    html_path = tmp_path / "report.html"
    # Don't create the file
    service.html_exporter.export = MagicMock(return_value=html_path)
    
    res = service.export_document(src, formats=["docx"])
    
    # HTML logic runs (docx requires html), returns path.
    # Then docx logic checks if html_path.exists(). It doesn't.
    assert res == []

def test_export_cleanup_error(service, tmp_path):
    # HTML not requested, but needed for DOCX. Cleanup triggers.
    src = tmp_path / "report.md"
    src.write_text("content")
    
    html_path = (tmp_path / "report.html")
    html_path.touch()
    
    service.html_exporter.export = MagicMock(return_value=html_path)
    service.docx_exporter.export = MagicMock(return_value=tmp_path / "report.docx")
    
    # Mock unlink to raise Error logic in cleanup block
    # Logic: if "html" not in formats and "docx" in formats and html_path
    
    # We patch Path.unlink? But patching built-ins is tricky.
    # Actually, export_service just passes 'pass' in except block line 98
    # So we just verify it doesn't crash.
    
    with patch("pathlib.Path.unlink", side_effect=PermissionError):
         # formats=["docx"] -> implies validation HTML needed but not kept
         res = service.export_document(src, formats=["docx"])
         assert len(res) == 1 # DOCX generated
         # HTML should still exist if unlink failed?
         # Or mock unlink is called.

# --- TabBasedHTMLExporter (Unused module) ---

def test_tab_exporter_basic():
    exporter = TabBasedHTMLExporter()
    sections = [
        {"id": "s1", "title": "Section 1", "content": "<p>Content 1</p>"},
        {"id": "s2", "title": "Section 2", "content": "<p>Content 2</p>"}
    ]
    info = {"name": "Test", "grade": "A"}
    
    html = exporter._build_html_document(sections, info)
    
    assert "<!DOCTYPE html>" in html
    assert "Section 1" in html
    assert 'id="s1"' in html
    assert "Section 2" in html
    
    # Check CSS/JS injection
    assert ".dashboard-header" in html
    assert "document.querySelectorAll" in html

def test_tab_exporter_single_section():
    exporter = TabBasedHTMLExporter()
    sections = [{"id": "s1", "title": "One", "content": "C"}]
    html = exporter._build_html_document(sections, {})
    assert "One" in html
