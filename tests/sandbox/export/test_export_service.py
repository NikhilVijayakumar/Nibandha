
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
from nibandha.configuration.infrastructure.file_loader import FileConfigLoader
from nibandha.configuration.domain.models.app_config import AppConfig

def test_export_document_html_only(export_sandbox):
    """Test exporting only HTML."""
    # Only override filename, use defaults (absolute paths) for dirs
    env = create_sandbox_env(export_sandbox, {"export": {"formats": ["html"], "output_filename": "doc"}})
    
    # Create input file IN the input directory for visibility
    input_file = env['input'] / "test_doc.md"
    input_file.write_text("# Test Document\n\nContent", encoding="utf-8")
    
    loader = FileConfigLoader()
    app_config = loader.load(env['config_path'], AppConfig)
    
    service = ExportService(app_config.export)
    
    # Export specific file
    generated = service.export_document(input_file)
    
    assert len(generated) == 1
    assert generated[0].name == "doc.html"
    assert generated[0].exists()
    assert generated[0].parent.resolve() == env['output'].resolve()
    assert "Test Document" in generated[0].read_text(encoding="utf-8")

def test_export_document_docx_mocked(export_sandbox, mock_pypandoc):
    """Test exporting DOCX with mocked pypandoc."""
    env = create_sandbox_env(export_sandbox, {
        "export": {
            "formats": ["docx", "html"], 
            "output_filename": "doc"
        }
    })
    
    # Create input file IN the input directory for visibility
    input_file = env['input'] / "test_doc.md"
    input_file.write_text("# Test Document\n\nContent", encoding="utf-8")
    
    loader = FileConfigLoader()
    app_config = loader.load(env['config_path'], AppConfig)
    
    service = ExportService(app_config.export)
    
    generated = service.export_document(input_file)
    
    assert len(generated) == 2
    filenames = {p.name for p in generated}
    assert "doc.html" in filenames
    assert "doc.docx" in filenames
    
    for p in generated:
        assert p.exists()
        assert p.parent.resolve() == env['output'].resolve()

def test_export_unified_default_order(export_sandbox):
    """Test unified export default file ordering (Alphabetical)."""
    # Create env with default config first to ensure dirs exist
    env = create_sandbox_env(export_sandbox, {
        "export": {
            "formats": ["html"], 
            "output_filename": "unified_report"
        }
    })
    
    # Setup multiple files
    (env['input'] / "z_last.md").write_text("# Last\nContent", encoding="utf-8")
    (env['input'] / "a_first.md").write_text("# First\nContent", encoding="utf-8")
    
    loader = FileConfigLoader()
    app_config = loader.load(env['config_path'], AppConfig)
    
    service = ExportService(app_config.export)
    
    # Run unified export
    results = service.export_unified()
    
    # Should create unified_report.html
    html_path = env['output'] / "unified_report.html"
    assert html_path.exists()
    assert html_path in results
    
    # Check content order
    content = html_path.read_text(encoding="utf-8")
    # "First" should appear before "Last"
    # Note: Depending on template, title might be used.
    # a_first.md title is "First", z_last.md title is "Last".
    # Alphabetical order of filenames: a_first.md -> z_last.md.
    # So "First" content comes first.
    assert content.find("First") < content.find("Last")

def test_export_unified_custom_order(export_sandbox):
    """Test unified export with custom export_order."""
    # Order: 3 -> 1 -> 2
    env = create_sandbox_env(export_sandbox, {
        "export": {
            "formats": ["html"],
            "output_filename": "ordered_report",
            "export_order": ["part3", "part1", "part2"]
        }
    })
    
    (env['input'] / "part1.md").write_text("# Part 1", encoding="utf-8")
    (env['input'] / "part2.md").write_text("# Part 2", encoding="utf-8")
    (env['input'] / "part3.md").write_text("# Part 3", encoding="utf-8")
    
    loader = FileConfigLoader()
    app_config = loader.load(env['config_path'], AppConfig)
    service = ExportService(app_config.export)
    
    service.export_unified()
    
    html_path = env['output'] / "ordered_report.html"
    assert html_path.exists()
    
    content = html_path.read_text(encoding="utf-8")
    p1 = content.find("Part 1")
    p2 = content.find("Part 2")
    p3 = content.find("Part 3")
    
    assert p3 < p1
    assert p1 < p2

def test_export_unified_exclusions(export_sandbox):
    """Test unified export respects exclude_files."""
    env = create_sandbox_env(export_sandbox, {
        "export": {
            "formats": ["html"],
            "output_filename": "filtered_report",
            "exclude_files": ["skip"]
        }
    })
    
    (env['input'] / "keep.md").write_text("# Keep", encoding="utf-8")
    (env['input'] / "skip.md").write_text("# Skip", encoding="utf-8")
    
    loader = FileConfigLoader()
    app_config = loader.load(env['config_path'], AppConfig)
    service = ExportService(app_config.export)
    
    service.export_unified()
    
    html_path = env['output'] / "filtered_report.html"
    content = html_path.read_text(encoding="utf-8")
    
    assert "Keep" in content
    assert "Skip" not in content

