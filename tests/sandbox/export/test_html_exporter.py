
import pytest
from pathlib import Path
from nibandha.export.infrastructure.html_exporter import HTMLExporter

from tests.sandbox.export.utils import create_sandbox_env

def test_html_export_basic(export_sandbox):
    """Test basic markdown to HTML conversion."""
    exporter = HTMLExporter()
    
    # Setup environment
    env = create_sandbox_env(export_sandbox, {"export": {"formats": ["html"], "output_filename": "basic"}})
    input_dir = env['input']
    output_dir = env['output']

    import json
    config_path = env['config_path']
    with open(config_path, 'r') as f:
        config_data = json.load(f)
    fname = config_data['export']['output_filename']

    content = "# Hello\n\n* world"
    output = output_dir / f"{fname}.html"
    
    result = exporter.export(content, output)
    
    assert result.exists()
    text = result.read_text(encoding="utf-8")
    assert "<h1>Hello</h1>" in text or "<h1 id=\"hello\">Hello</h1>" in text
    assert "<li>world</li>" in text

def test_html_export_styling(export_sandbox):
    """Test that styling is injected."""
    # Setup environment
    env = create_sandbox_env(export_sandbox, {"export": {"formats": ["html"], "output_filename": "styled"}})
    input_dir = env['input']
    output_dir = env['output']
    
    import json
    config_path = env['config_path']
    with open(config_path, 'r') as f:
        config_data = json.load(f)
    fname = config_data['export']['output_filename']
    
    # Create a dummy style
    style_dir = input_dir / "styles"
    style_dir.mkdir()
    (style_dir / "custom.css").write_text("body { color: red; }")
    
    exporter = HTMLExporter(style_dir=style_dir)
    
    content = "# Styled"
    output = output_dir / f"{fname}.html"
    
    result = exporter.export(content, output, style="custom")
    
    text = result.read_text(encoding="utf-8")
    assert "color: red" in text

def test_docx_friendly_preprocessing():
    """Test the cleanup logic for docx compatibility."""
    exporter = HTMLExporter()
    dirty_html = "<p><br /></p>\n  \n  \n<p>Content</p>"
    clean_html = exporter._make_docx_friendly(dirty_html)
    
    assert "<p>&nbsp;</p>" in clean_html
    assert "\n\n<p>Content</p>" in clean_html

