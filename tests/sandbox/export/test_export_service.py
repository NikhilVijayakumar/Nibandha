
import pytest
from pathlib import Path
from nibandha.export.application.export_service import ExportService
from nibandha.configuration.domain.models.export_config import ExportConfig

def test_export_service_initialization(export_config):
    """Verify service initializes with valid config."""
    service = ExportService(export_config)
    assert service.config == export_config
    assert service.html_exporter is not None
    assert service.docx_exporter is not None

def test_export_service_validation_failure():
    """Verify validation fails if output_dir missing."""
    invalid_config = ExportConfig(output_dir=None)
    with pytest.raises(ValueError, match="output_dir is required"):
        ExportService(invalid_config)

from tests.sandbox.export.utils import create_sandbox_env

def test_export_document_html_only(export_sandbox, sample_markdown):
    """Test exporting only HTML."""
    env = create_sandbox_env(export_sandbox, {"export": {"formats": ["html"]}})
    output_dir = env['output'] / "html_out"
    output_dir.mkdir(parents=True, exist_ok=True)
    config = ExportConfig(
        formats=["html"],
        output_dir=output_dir,
        output_filename="doc"
    )
    service = ExportService(config)
    
    generated = service.export_document(sample_markdown)
    
    assert len(generated) == 1
    assert generated[0].name == "doc.html"
    assert generated[0].exists()
    assert "Test Document" in generated[0].read_text(encoding="utf-8")

def test_export_document_docx_mocked(export_sandbox, sample_markdown, mock_pypandoc):
    """Test exporting DOCX with mocked pypandoc."""
    env = create_sandbox_env(export_sandbox, {"export": {"formats": ["docx", "html"]}}) # html required for docx
    output_dir = env['output'] / "docx_out"
    output_dir.mkdir(parents=True, exist_ok=True)
    config = ExportConfig(
        formats=["docx", "html"], # HTML explicitly required now
        output_dir=output_dir,
        output_filename="doc"
    )
    service = ExportService(config)
    
    generated = service.export_document(sample_markdown)
    
    # improved: wait, formats=["docx"] might NOT implicitly create HTML in the output list returned?
    # actually implementation logic: 
    # if needs_html: generates HTML. 
    # if "html" in formats: adds to generated_files.
    # if "docx" in formats: adds docx to generated_files.
    # So if formats=["docx"], list should contain 1 file (docx). HTML is temp intermediate unless requested.
    
    # Wait, looking at implementation:
    # if html_path: if "html" in formats: generated_files.append(html_path)
    # So HTML is NOT returned if not requested? Correct.
    
    assert len(generated) == 2
    filenames = {p.name for p in generated}
    assert "doc.html" in filenames
    assert "doc.docx" in filenames
    
    for p in generated:
        assert p.exists()

def test_export_batch(export_sandbox):
    """Test batch export of multiple files."""
    env = create_sandbox_env(export_sandbox, {"export": {"formats": ["html"]}})
    input_dir = env['input']
    output_dir = env['output'] / "batch_out"
    output_dir.mkdir()
    
    # Create multiple MD files
    (input_dir / "doc1.md").write_text("# Doc 1")
    (input_dir / "doc2.md").write_text("# Doc 2")
    
    config = ExportConfig(
        formats=["html"],
        output_dir=output_dir,
        # input_dir logic uses FileDiscovery. If not set, might fail?
        # FileDiscovery defaults?
        # Let's see ExportService.export_batch implementation.
        input_dir=input_dir 
    )
    service = ExportService(config)
    
    # We need to mock FileDiscovery or set input_dir in config.
    # AppConfig usually sets input_dir default. Here we manually set it.
    
    results = service.export_batch()
    
    assert "doc1" in results
    assert "doc2" in results
    assert (output_dir / "doc1.html").exists()
    assert (output_dir / "doc2.html").exists()

