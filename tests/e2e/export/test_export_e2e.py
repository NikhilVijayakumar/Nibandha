
import pytest
from pathlib import Path
from nibandha.export.infrastructure.html_tab_exporter import TabBasedHTMLExporter
from nibandha.export.infrastructure.modern_dashboard_exporter import ModernDashboardExporter

@pytest.fixture
def sample_markdown_sections():
    return [
        {"title": "Section 1", "content": "# Header 1\nText content."},
        {"title": "Section 2", "content": "## Subheader\nMore text."}
    ]

@pytest.fixture
def project_info():
    return {
        "name": "E2E Test Project",
        "grade": "A",
        "status": "Passing"
    }

def test_html_tab_export_EXP_E2E_001(tmp_path, sample_markdown_sections, project_info):
    """Verify TabBasedHTMLExporter generates file."""
    exporter = TabBasedHTMLExporter()
    output_path = tmp_path / "report_tabs.html"
    
    result = exporter.export(sample_markdown_sections, output_path, project_info)
    
    assert result.exists()
    assert result.stat().st_size > 0
    content = result.read_text("utf-8")
    assert "<!DOCTYPE html>" in content
    assert "Section 1" in content

def test_modern_dashboard_export_EXP_E2E_002(tmp_path, sample_markdown_sections, project_info):
    """Verify ModernDashboardExporter generates file."""
    exporter = ModernDashboardExporter()
    output_path = tmp_path / "report_dashboard.html"
    
    result = exporter.export(sample_markdown_sections, output_path, project_info)
    
    assert result.exists()
    assert result.stat().st_size > 0
    content = result.read_text("utf-8")
    assert "sidebar" in content  # Dashboard specific
    assert "Section 1" in content
