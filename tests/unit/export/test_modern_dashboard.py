
import pytest
from pathlib import Path
from nibandha.export.infrastructure.modern_dashboard_exporter import ModernDashboardExporter

class TestModernDashboardExporter:
    
    @pytest.fixture
    def exporter(self):
        return ModernDashboardExporter()
        
    def test_export_happy_path_structure(self, exporter, tmp_path):
        """EXP-UT-006: Verify dashboard structure generation."""
        sections = [
            {
                "title": "Summary", 
                "content": "# Summary Content", 
                "metrics_cards": []
            },
            {
                "title": "Details",
                "content": "## Detail Content",
                "metrics_cards": []
            }
        ]
        
        output = tmp_path / "dashboard.html"
        res = exporter.export(sections, output, {"name": "TestProj", "grade": "A"})
        
        assert res.exists()
        text = res.read_text()
        
        # Verify Key Structural Elements
        assert '<!DOCTYPE html>' in text
        assert '<nav class="sidebar-nav">' in text
        assert '<aside class="sidebar">' in text
        assert '<main class="main-content">' in text
        
        # Verify Content rendering
        # Markdown should be converted
        assert '<h1>Summary Content</h1>' in text or '<h1 id="summary-content">' in text
        
        # Verify Navigation IDs
        # id="summary" derived from title
        assert 'id="summary"' in text
        assert 'href="#summary"' in text
        
    def test_metrics_rendering(self, exporter, tmp_path):
        """EXP-UT-007: Verify metrics cards rendering."""
        sections = [{
            "title": "Metrics",
            "content": "text",
            "metrics_cards": [
                {"title": "Coverage", "value": "80%", "color": "green", "icon": "C"},
                {"title": "Bugs", "value": "0"} 
            ]
        }]
        
        output = tmp_path / "metrics.html"
        exporter.export(sections, output)
        text = output.read_text()
        
        assert '<div class="metrics-grid">' in text
        assert 'card-green' in text
        assert '80%' in text
        assert 'Coverage' in text
        assert 'card-blue' in text # Default color
        
    def test_project_info_defaults(self, exporter, tmp_path):
        """EXP-UT-009: Verify defaults when project info is missing."""
        sections = [{"title": "A", "content": "B"}]
        output = tmp_path / "defaults.html"
        
        # Pass None for project_info
        exporter.export(sections, output, None)
        text = output.read_text()
        
        assert "Quality Report" in text # Def Name
        assert "class=\"grade-badge grade-f\"" in text.lower() or "grade-n/a" in text.lower()
        
    def test_empty_corner_cases(self, exporter, tmp_path):
        """EXP-UT-008: Verify empty sections list handles gracefully."""
        output = tmp_path / "empty.html"
        exporter.export([], output)
        text = output.read_text()
        
        assert '<nav class="sidebar-nav">' in text
        # Should be valid HTML frame
        assert '<body' in text
        
    def test_css_js_injection(self, exporter, tmp_path):
        """Verify CSS and JS are injected."""
        output = tmp_path / "assets.html"
        exporter.export([{"title": "A", "content": "B"}], output)
        text = output.read_text()
        
        assert "Modern Dashboard Layout" in text # CSS comment
        assert "theme-toggle" in text # JS function
        assert "document.querySelectorAll" in text
