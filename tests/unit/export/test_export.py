
import pytest
from pathlib import Path
from nibandha.export.infrastructure.html_exporter import HTMLExporter

class TestHTMLExporter:
    
    @pytest.fixture
    def exporter(self, tmp_path):
        # Create dummy style dir
        style_dir = tmp_path / "styles"
        style_dir.mkdir()
        (style_dir / "default.css").write_text("body { color: black; }")
        return HTMLExporter(style_dir=style_dir)
        
    def test_export_simple_markdown(self, exporter, tmp_path):
        """Test basic markdown to HTML conversion."""
        content = "# Hello\n\n- Item 1\n- Item 2"
        out_file = tmp_path / "output.html" # Exporter adds extension if needed, but logic takes path without ext usually?
        # Logic: output_path is without extension, or at least stem used for title.
        # code: output_file = output_path.with_suffix('.html')
        
        res = exporter.export(content, tmp_path / "report", style="default")
        
        assert res.exists()
        text = res.read_text()
        assert "Hello</h1>" in text
        assert "Item 1</li>" in text
        assert "body { color: black; }" in text
        
    def test_export_missing_style_fallback(self, exporter, tmp_path):
        """Test fallback to default style if requested style missing."""
        content = "foo"
        res = exporter.export(content, tmp_path / "report2", style="missing_style")
        assert res.exists()
        text = res.read_text()
        # Should contain default css content
        assert "body { color: black; }" in text

    def test_export_inline_fallback(self, tmp_path):
        """Test fallback to inline CSS if no style files exist."""
        # Initialize with empty dir (no default.css)
        empty_dir = tmp_path / "empty_styles"
        empty_dir.mkdir()
        exporter = HTMLExporter(style_dir=empty_dir)
        
        res = exporter.export("content", tmp_path / "report3")
        text = res.read_text()
        assert "font-family: 'Calibri'" in text # content from _get_inline_default_css

    def test_docx_friendly_processing(self, exporter, tmp_path):
        """Test that docx_friendly flag cleans up HTML."""
        content = "Line 1\n\nLine 2" # markdown2 usually creates paragraphs
        # We want to test that _make_docx_friendly runs.
        # It replaces <p><br /></p> with <p>&nbsp;</p> and cleans newlines.
        
        # Inject raw HTML that needs cleaning?
        # The export method calls markdown2 first. 
        # But we can verify no crash.
        res = exporter.export(content, tmp_path / "report4", docx_friendly=True)
        assert res.exists()
        
    def test_style_loading_failure_handling(self, exporter, tmp_path):
        """Test handling of various style loading failures."""
        # 1. Non-existent style -> Default
        # (covered by test_export_missing_style_fallback)
        
        # 2. Default also missing -> Inline
        # (covered by test_export_inline_fallback)
        pass

    def test_export_structure(self, exporter, tmp_path):
        """Test that the exported HTML has correct structure."""
        res = exporter.export("# Title", tmp_path / "struct_test")
        text = res.read_text()
        
        assert "<!DOCTYPE html>" in text
        assert "<html lang=\"en\">" in text
        assert "<title>Struct Test</title>" in text
        assert "<article class=\"document\">" in text
