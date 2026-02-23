"""Helper class for processing mermaid diagrams in markdown."""
import re
import logging
from typing import Dict, Tuple

logger = logging.getLogger("nibandha.export.helpers.mermaid")


class MermaidProcessor:
    """
    Handles extraction, protection, and restoration of mermaid blocks.
    
    Prevents markdown2 from corrupting mermaid syntax (especially quotes, 
    brackets, and HTML entities) and converts them to JS-friendly divs or 
    fallback messages for DOCX.
    """
    
    # Regex to find ```mermaid ... ``` blocks
    # Uses DOTALL to match across newlines
    MERMAID_PATTERN = re.compile(r'```mermaid\s*\n(.*?)\n```', re.DOTALL)
    
    # Regex to find placeholders in HTML output
    PLACEHOLDER_PATTERN = re.compile(r'<!-- MERMAID_PLACEHOLDER_(\d+) -->')
    
    @staticmethod
    def pre_process(markdown_content: str) -> Tuple[str, Dict[str, str]]:
        """
        Extract mermaid blocks and replace with placeholders.
        
        Args:
            markdown_content: Raw markdown text
            
        Returns:
            Tuple of (processed markdown, dictionary mapping placeholder ID to original code)
        """
        store = {}
        counter = 0
        
        def replace_match(match):
            nonlocal counter
            code = match.group(1).strip()
            placeholder = f"<!-- MERMAID_PLACEHOLDER_{counter} -->"
            store[str(counter)] = code
            counter += 1
            return f"\n\n{placeholder}\n\n"
            
        processed = MermaidProcessor.MERMAID_PATTERN.sub(replace_match, markdown_content)
        return processed, store

    @staticmethod
    def post_process(html_content: str, store: Dict[str, str]) -> str:
        """
        Restore mermaid blocks as divs for HTML rendering.
        
        Args:
            html_content: HTML text with placeholders
            store: Dictionary mapping placeholder ID to original code
            
        Returns:
            HTML with valid <div class="mermaid"> elements
        """
        def replace_placeholder(match):
            uid = match.group(1)
            code = store.get(uid, "")
            # Return raw code wrapped in mermaid div
            # Do NOT escape quotes/HTML as Mermaid JS needs the raw syntax
            return f'<div class="mermaid">\n{code}\n</div>'
            
        # Due to how markdown2 might wrap the placeholder in <p> tags
        # we also need to clean up any leftover <p> wrapper around our div
        processed = MermaidProcessor.PLACEHOLDER_PATTERN.sub(replace_placeholder, html_content)
        
        # Clean up possible <p> wrappers added by markdown2 around our comment placeholder
        # which would now be wrapped around out <div class="mermaid">
        processed = re.sub(r'<p>\s*(<div class="mermaid">.*?</div>)\s*</p>', r'\1', processed, flags=re.DOTALL)
        
        return processed

    @staticmethod
    def convert_to_image_tags(html_content: str) -> str:
        """
        Convert mermaid divs to graceful fallback notices for DOCX export.
        
        Args:
            html_content: HTML containing <div class="mermaid">
            
        Returns:
            HTML with fallback messages
        """
        # Find all <div class="mermaid">...</div> using regex
        # Using non-greedy match to find individual blocks
        mermaid_div_pattern = re.compile(r'<div class="mermaid">\s*(.*?)\s*</div>', re.DOTALL)
        
        def fallback_replacement(match):
            return (
                '<div style="border: 1px dashed #ccc; padding: 10px; color: #666; font-style: italic; background: #f9f9f9; margin: 10px 0;">'
                '<strong>[Diagram Placeholder]</strong><br/>'
                '<em>Mermaid diagrams represent complex logic or architecture. Please view the HTML version of this report to see the interactive diagram.</em>'
                '</div>'
            )
            
        return mermaid_div_pattern.sub(fallback_replacement, html_content)
