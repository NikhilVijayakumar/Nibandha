import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock
from nibandha.configuration.domain.models.export_config import ExportConfig

@pytest.fixture
def mock_pypandoc(monkeypatch):
    """
    Mock pypandoc to simulate successful DOCX conversion without actual pandoc installed.
    """
    mock = MagicMock()
    # Mock get_pandoc_version to return a valid version string
    mock.get_pandoc_version.return_value = "2.19.2"
    # Mock convert_file to simulate creating the file
    def side_effect(source_file, to, outputfile, extra_args=None):
        Path(outputfile).touch()
        return outputfile
    mock.convert_file.side_effect = side_effect
    
    # Apply patch to where it is imported in docx_exporter
    # Note: If it's imported as 'import pypandoc', we patch sys.modules or the module attribute
    # In docx_exporter.py: "import pypandoc" inside try/except block in _check_dependencies
    # Typically harder to patch local import. Better to patch the class attribute if possible or use sys.modules
    
    monkeypatch.setitem(sys.modules, 'pypandoc', mock)
    return mock

@pytest.fixture
def export_sandbox(sandbox_root):
    """
    Creates a dedicated export sandbox environment.
    """
    export_dir = sandbox_root / "export_test"
    export_dir.mkdir(parents=True, exist_ok=True)
    return export_dir

@pytest.fixture
def sample_markdown(export_sandbox):
    """
    Creates a sample markdown file for testing.
    """
    content = """
# Test Document

## Introduction
This is a test markdown document.
- Item 1
- Item 2

## Code Section
```python
print("Hello World")
```
"""
    md_file = export_sandbox / "test_doc.md"
    md_file.write_text(content.strip(), encoding="utf-8")
    return md_file

@pytest.fixture
def export_config(export_sandbox):
    """
    Standard ExportConfig pointing to sandbox directory.
    """
    return ExportConfig(
        formats=["html", "docx"],
        style="default",
        output_dir=export_sandbox / "output",
        output_filename="test_output"
    )
