import pytest
from nibandha.export.application.helpers.math_processor import MathProcessor

def test_extract_block_math():
    markdown = "Here is some math:\n\n$$ \nE=mc^2 \n$$\nEnd"
    content, store = MathProcessor.pre_process(markdown)
    
    assert "<!-- MATH_PLACEHOLDER_0 -->" in content
    assert "$$" not in content
    assert "0" in store
    assert store["0"] == ('block', 'E=mc^2')

def test_extract_inline_math():
    markdown = "Price is $100 and equation is $x+y=z$"
    content, store = MathProcessor.pre_process(markdown)
    
    # Needs to extract equation, not price
    assert "<!-- MATH_PLACEHOLDER_0 -->" in content
    assert "$x+y=z$" not in content
    assert "Price is $100" in content
    assert "0" in store
    assert store["0"] == ('inline', 'x+y=z')
    
def test_restore_block_math():
    html = "<p>Here is some math:</p>\n<!-- MATH_PLACEHOLDER_0 -->\n<p>End</p>"
    store = {"0": ('block', 'E=mc^2')}
    
    restored = MathProcessor.post_process(html, store)
    
    assert '<span class="math display">\\[E=mc^2\\]</span>' in restored
    assert "<!-- MATH_PLACEHOLDER_0 -->" not in restored

def test_restore_inline_math():
    html = "<p>Equation is <!-- MATH_PLACEHOLDER_0 --></p>"
    store = {"0": ('inline', 'x+y=z')}
    
    restored = MathProcessor.post_process(html, store)
    
    assert '<span class="math inline">\\(x+y=z\\)</span>' in restored
    assert "<!-- MATH_PLACEHOLDER_0 -->" not in restored

def test_extract_escaped_brackets_math():
    markdown = "Block math: \\[ \\mu = \\alpha \\]\nInline math: \\( \\beta = 1 \\)"
    content, store = MathProcessor.pre_process(markdown)
    
    assert "<!-- MATH_PLACEHOLDER_0 -->" in content
    assert "<!-- MATH_PLACEHOLDER_1 -->" in content
    assert "0" in store
    assert store["0"] == ("block", "\\mu = \\alpha")
    assert "1" in store
    assert store["1"] == ("inline", "\\beta = 1")
