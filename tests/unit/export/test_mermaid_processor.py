import pytest
from nibandha.export.application.helpers.mermaid_processor import MermaidProcessor

def test_pre_process_extracts_mermaid_blocks():
    """Test that mermaid blocks are extracted and replaced with placeholders."""
    markdown = """
# Some Title
Here is a diagram:

```mermaid
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
```

And some text after.
"""
    processed, store = MermaidProcessor.pre_process(markdown)
    
    assert "<!-- MERMAID_PLACEHOLDER_0 -->" in processed
    assert "graph TD" not in processed
    assert len(store) == 1
    assert "0" in store
    assert "graph TD;" in store["0"]

def test_pre_process_no_mermaid():
    """Test that markdown without mermaid is unchanged."""
    markdown = "# Title\nJust text\n```python\nprint('hello')\n```"
    processed, store = MermaidProcessor.pre_process(markdown)
    
    assert processed == markdown
    assert len(store) == 0

def test_post_process_replaces_placeholders():
    """Test that placeholders are restored as mermaid divs."""
    html = "<p>Here is text</p>\n<!-- MERMAID_PLACEHOLDER_0 -->\n<p>More text</p>"
    store = {"0": "graph TD;\nA-->B;"}
    
    processed = MermaidProcessor.post_process(html, store)
    
    assert '<div class="mermaid">' in processed
    assert "graph TD;\nA-->B;" in processed
    assert "<!-- MERMAID_PLACEHOLDER_0 -->" not in processed

def test_post_process_cleans_paragraph_wrappers():
    """Test that markdown2's paragraph wrappers around the placeholder are cleaned."""
    html = "<p>Text</p>\n<p><!-- MERMAID_PLACEHOLDER_0 --></p>\n<p>More</p>"
    store = {"0": "graph TD;"}
    
    processed = MermaidProcessor.post_process(html, store)
    
    assert '<div class="mermaid">' in processed
    assert '<p><div class="mermaid">' not in processed
    assert '</div></p>' not in processed

def test_convert_to_image_tags():
    """Test converting to fallback messages for DOCX."""
    html = '<h1>Title</h1><div class="mermaid">\ngraph TD;\n</div><p>Text</p>'
    
    processed = MermaidProcessor.convert_to_image_tags(html)
    
    assert '<div class="mermaid">' not in processed
    assert "graph TD;" not in processed
    assert "[Diagram Placeholder]" in processed
    assert "Mermaid diagrams represent complex logic" in processed

def test_multiple_mermaid_blocks():
    """Test processing multiple mermaid blocks."""
    markdown = """
# Title
```mermaid
graph TD;
```
Text
```mermaid
sequenceDiagram
```
"""
    processed, store = MermaidProcessor.pre_process(markdown)
    
    assert "<!-- MERMAID_PLACEHOLDER_0 -->" in processed
    assert "<!-- MERMAID_PLACEHOLDER_1 -->" in processed
    assert len(store) == 2
    
    html = f"<p>Text</p>\n{processed}"
    final_html = MermaidProcessor.post_process(html, store)
    
    assert '<div class="mermaid">\ngraph TD;\n</div>' in final_html
    assert '<div class="mermaid">\nsequenceDiagram\n</div>' in final_html
