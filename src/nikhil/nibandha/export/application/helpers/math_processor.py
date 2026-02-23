"""Helper class for processing LaTeX math in markdown."""
import re
import logging
from typing import Dict, Tuple

logger = logging.getLogger("nibandha.export.helpers.math")

class MathProcessor:
    """
    Handles extraction and restoration of LaTeX math blocks.
    
    Prevents markdown2 from interpreting LaTeX elements (like _, ^, etc.) 
    as markdown formatting, and converts them to standard formats for 
    Pandoc/MathJax.
    """
    
    # Block math: $$...$$ or \[...\]
    BLOCK_MATH_PATTERN = re.compile(r'(\$\$|\\\[)(.*?)(\$\$|\\\])', re.DOTALL)
    
    # Inline math: $...$ or \(...\)
    # Be careful not to match simple $ prices or non-math content.
    # It must not have whitespace right after opening $ or right before closing $.
    # And it cannot contain $.
    INLINE_MATH_PATTERN = re.compile(r'(?<!\\)\$(?!\s)([^$\n\r]+?)(?<!\s)\$|\\\((.*?)\\\)', re.DOTALL)
    
    PLACEHOLDER_PATTERN = re.compile(r'<!-- MATH_PLACEHOLDER_(\d+) -->')
    
    @staticmethod
    def pre_process(markdown_content: str) -> Tuple[str, Dict[str, Tuple[str, str]]]:
        """
        Extract math blocks and replace with placeholders.
        
        Args:
            markdown_content: Raw markdown text
            
        Returns:
            Tuple of (processed markdown, dictionary mapping placeholder ID to (type, original code))
            type is either 'block' or 'inline'.
        """
        store = {}
        counter = 0
        
        def replace_block_match(match):
            nonlocal counter
            code = match.group(2).strip()
            placeholder = f"<!-- MATH_PLACEHOLDER_{counter} -->"
            store[str(counter)] = ('block', code)
            counter += 1
            return f"\n\n{placeholder}\n\n"
            
        def replace_inline_match(match):
            nonlocal counter
            # Group 1 is for $...$, Group 2 is for \(...\)
            code = match.group(1) if match.group(1) is not None else match.group(2)
            if code is None:
                code = ""
            code = code.strip()
            placeholder = f"<!-- MATH_PLACEHOLDER_{counter} -->"
            store[str(counter)] = ('inline', code)
            counter += 1
            return placeholder
            
        # First process blocks, then inline to avoid inline capturing parts of blocks
        processed = MathProcessor.BLOCK_MATH_PATTERN.sub(replace_block_match, markdown_content)
        processed = MathProcessor.INLINE_MATH_PATTERN.sub(replace_inline_match, processed)
        
        return processed, store

    @staticmethod
    def post_process(html_content: str, store: Dict[str, Tuple[str, str]]) -> str:
        """
        Restore math blocks as MathJax/Pandoc compatible LaTeX markers.
        
        Args:
            html_content: HTML text with placeholders
            store: Dictionary mapping placeholder ID to original code
            
        Returns:
            HTML with restored math blocks
        """
        def replace_placeholder(match):
            uid = match.group(1)
            math_type, code = store.get(uid, ('inline', ''))
            
            if math_type == 'block':
                return f'<span class="math display">\\[{code}\\]</span>'
            else:
                return f'<span class="math inline">\\({code}\\)</span>'
                
        processed = MathProcessor.PLACEHOLDER_PATTERN.sub(replace_placeholder, html_content)
        
        # markdown2 might wrap block placeholders in <p> tags, which is fine, but
        # the display math shouldn't really be inside <p>. However, MathJax and Pandoc handle it.
        # Alternatively, we can let Pandoc parse the math display class.
        
        return processed
