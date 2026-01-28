
import pytest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
from nibandha.export.application.export_service import ExportService

class TestExportService:
    
    @pytest.fixture
    def mock_exporters(self):
        with patch("nibandha.export.application.export_service.HTMLExporter") as MockHTML, \
             patch("nibandha.export.application.export_service.DOCXExporter") as MockDOCX, \
             patch("nibandha.export.application.export_service.ModernDashboardExporter") as MockDash:
            
            yield MockHTML, MockDOCX, MockDash
            
    def test_service_init(self, mock_exporters):
        """Test service initializes exporters."""
        MockHTML, MockDOCX, MockDash = mock_exporters
        ExportService()
        MockHTML.assert_called_once()
        MockDOCX.assert_called_once()
        MockDash.assert_called_once()
        
    def test_export_document_html(self, mock_exporters, tmp_path):
        """Test basic document export to HTML."""
        MockHTML, _, _ = mock_exporters
        mock_html = MockHTML.return_value
        mock_html.export.return_value = tmp_path / "doc.html"
        
        service = ExportService()
        p = tmp_path / "doc.md"
        p.write_text("content")
        
        res = service.export_document(p, ["html"])
        
        assert len(res) == 1
        assert res[0] == tmp_path / "doc.html"
        mock_html.export.assert_called()
        
    def test_export_document_docx(self, mock_exporters, tmp_path):
        """Test basic document export to DOCX flows through HTML."""
        MockHTML, MockDOCX, _ = mock_exporters
        mock_html = MockHTML.return_value
        mock_docx = MockDOCX.return_value
        
        mock_html.export.return_value = tmp_path / "doc.html"
        mock_docx.export.return_value = tmp_path / "doc.docx"
        # Mock file existence check if needed, but mocks return paths
        
        service = ExportService()
        p = tmp_path / "doc.md"
        p.write_text("content")
        
        # Mock existence of intermediate html
        with patch("pathlib.Path.exists", return_value=True):
             res = service.export_document(p, ["docx"])
        
        assert len(res) == 1
        assert res[0] == tmp_path / "doc.docx"
        mock_html.export.assert_called() # Intermediate
        mock_docx.export.assert_called()
        
    def test_export_unified_report_html(self, mock_exporters, tmp_path):
        """Test unified report uses Dashboard Exporter for HTML."""
        _, _, MockDash = mock_exporters
        mock_dash = MockDash.return_value
        
        service = ExportService()
        
        # Setup input files
        summary = tmp_path / "summary.md"
        summary.write_text("---\ntitle: Sum\n---\nSummary content")
        
        detail = tmp_path / "detail.md"
        detail.write_text("---\ntitle: Det\n---\nDetail content")
        
        output_dir = tmp_path / "out"
        output_dir.mkdir()
        
        service.export_unified_report(summary, [detail], output_dir, ["html"])
        
        mock_dash.export.assert_called_once()
        args, _ = mock_dash.export.call_args
        sections = args[0]
        assert len(sections) == 2
        assert sections[0]['title'] == "Summary"
        assert sections[1]['title'] == "Detail"

    def test_export_unified_report_docx(self, mock_exporters, tmp_path):
        """Test unified report uses HTML->DOCX flow for DOCX."""
        MockHTML, MockDOCX, _ = mock_exporters
        mock_html = MockHTML.return_value
        mock_docx = MockDOCX.return_value
        
        service = ExportService()
        
        summary = tmp_path / "summary.md"
        summary.write_text("content")
        output_dir = tmp_path / "out"
        output_dir.mkdir()
        
        service.export_unified_report(summary, [], output_dir, ["docx"])
        
        # Should build unified markdown, convert to HTML, then DOCX
        mock_html.export.assert_called()
        mock_docx.export.assert_called()

    def test_remove_frontmatter(self, mock_exporters):
        """Test frontmatter removal logic."""
        service = ExportService()
        content = "---\nkey: value\n---\nReal content"
        clean = service._remove_frontmatter(content)
        # Implementation impl: joins lines[i+1:] which might drop the newline of the --- line?
        # lines = ["---", "key: value", "---", "Real content"]
        # i of 2nd "---" is 2. lines[i+1:] is ["Real content"]
        # join gives "Real content"
        assert clean == "Real content"
        
        content2 = "No frontmatter"
        clean2 = service._remove_frontmatter(content2)
        assert clean2 == "No frontmatter"

    def test_load_metrics_cards(self, mock_exporters, tmp_path):
        """Test loading metrics cards from JSON sidecar."""
        service = ExportService()
        
        # Structure: output/details/unit_report.md
        # JSON: output/assets/data/unit.json
        output = tmp_path / "output"
        details = output / "details"
        details.mkdir(parents=True)
        assets = output / "assets" / "data"
        assets.mkdir(parents=True)
        
        detail_md = details / "unit_report.md"
        json_file = assets / "unit.json"
        json_file.write_text('{"metrics_cards": [{"title": "Cov", "value": "100%"}]}')
        
        cards = service._load_metrics_cards(detail_md)
        assert len(cards) == 1
        assert cards[0]['title'] == "Cov"
