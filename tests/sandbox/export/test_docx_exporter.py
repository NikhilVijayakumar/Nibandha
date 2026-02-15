
import pytest
from pathlib import Path
from unittest.mock import MagicMock
from nibandha.export.infrastructure.docx_exporter import DOCXExporter

def test_docx_export_missing_dependency(monkeypatch):
    """Test explicit failure when pypandoc is missing."""
    # Simulate import error
    import builtins
    real_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == 'pypandoc':
            raise ImportError("Mocked missing pypandoc")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, '__import__', mock_import)
    
    # We must reload the module to trigger the check again? 
    # Or just instantiate a new one, as check is in __init__
    # But module level imports might cache it.
    # Actually DOCXExporter imports pypandoc INSIDE _check_dependencies method?
    # No, it imports it inside try/except block in _check_dependencies.
    
    exporter = DOCXExporter()
    assert not exporter.pypandoc_available
    
    result = exporter.export(Path("dummy.html"), Path("out.docx"))
    assert result is None

from tests.sandbox.export.utils import create_sandbox_env

def test_docx_export_success(export_sandbox, mock_pypandoc):
    """Test successful export flow with mocked pypandoc."""
    exporter = DOCXExporter()
    # verify mock injection worked
    assert exporter.pypandoc_available
    
    # Setup environment with AppConfig
    env = create_sandbox_env(export_sandbox, {"export": {"formats": ["docx"]}})
    input_dir = env['input']
    output_dir = env['output']

    # Create dummy source
    source = input_dir / "source.html"
    source.touch()
    output = output_dir / "final.docx"
    
    result = exporter.export(source, output)
    
    assert result == output
    # Verify mock was called correctly
    mock_pypandoc.convert_file.assert_called_once()
    args, kwargs = mock_pypandoc.convert_file.call_args
    assert kwargs['to'] == 'docx'
    assert kwargs['outputfile'] == str(output)

