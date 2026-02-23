
import pytest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
from nibandha.export.application.export_service import ExportService
from nibandha.configuration.domain.models.export_config import ExportConfig

class TestExportService:
    
    @pytest.fixture
    def export_config(self, tmp_path):
        """Create a test ExportConfig."""
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        (template_dir / "html").mkdir()
        (template_dir / "dashboard").mkdir()
        
        styles_dir = tmp_path / "styles"
        styles_dir.mkdir()
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        return ExportConfig(
            formats=["html", "docx"],
            style="default",
            template_dir=template_dir,
            styles_dir=styles_dir,
            output_dir=output_dir,
            output_filename="report"
        )
    
    @pytest.fixture
    def mock_exporters(self):
        with patch("nibandha.export.application.export_service.HTMLExporter") as MockHTML, \
             patch("nibandha.export.application.export_service.DOCXExporter") as MockDOCX, \
             patch("nibandha.export.application.export_service.ModernDashboardExporter") as MockDash:
            
            yield MockHTML, MockDOCX, MockDash
            
    def test_service_init(self, mock_exporters, export_config):
        """Test service initializes exporters with config paths."""
        MockHTML, MockDOCX, MockDash = mock_exporters
        ExportService(export_config)
        MockHTML.assert_called_once()
        MockDOCX.assert_called_once()
        MockDash.assert_called_once()
        
    def test_export_document_html(self, mock_exporters, export_config, tmp_path):
        """Test basic document export to HTML."""
        MockHTML, _, _ = mock_exporters
        mock_html = MockHTML.return_value
        mock_html.export.return_value = tmp_path / "report.html"
        
        service = ExportService(export_config)
        p = tmp_path / "doc.md"
        p.write_text("content")
        
        res = service.export_document(p)
        
        assert len(res) == 1
        mock_html.export.assert_called()
        
    def test_export_document_docx(self, mock_exporters, export_config, tmp_path):
        """Test basic document export to DOCX flows through HTML."""
        MockHTML, MockDOCX, _ = mock_exporters
        mock_html = MockHTML.return_value
        mock_docx = MockDOCX.return_value
        
        mock_html.export.return_value = export_config.output_dir / "report.html"
        mock_docx.export.return_value = export_config.output_dir / "report.docx"
        
        service = ExportService(export_config)
        p = tmp_path / "doc.md"
        p.write_text("content")
        
        # Mock existence of intermediate html
        with patch("pathlib.Path.exists", return_value=True):
             res = service.export_document(p)
        
        # Both HTML and DOCX in results since config specifies both formats
        assert len(res) == 2
        mock_html.export.assert_called() # Intermediate
        mock_docx.export.assert_called()
        
    def test_export_unified_report_html(self, mock_exporters, export_config, tmp_path):
        """Test unified report uses Dashboard Exporter for HTML."""
        _, _, MockDash = mock_exporters
        mock_dash = MockDash.return_value
        
        service = ExportService(export_config)
        
        # Setup input files
        summary = tmp_path / "summary.md"
        summary.write_text("---\ntitle: Sum\n---\nSummary content")
        
        detail = tmp_path / "detail.md"
        detail.write_text("---\ntitle: Det\n---\nDetail content")
        
        # Call with direct parameters
        service.export_unified_report(summary, [detail])
        
        mock_dash.export.assert_called_once()
        args, _ = mock_dash.export.call_args
        sections = args[0]
        assert len(sections) == 2
        assert sections[0]['title'] == "Summary"
        assert sections[1]['title'] == "Detail"

    def test_export_unified_report_docx(self, mock_exporters, export_config, tmp_path):
        """Test unified report uses HTML->DOCX flow for DOCX."""
        MockHTML, MockDOCX, _ = mock_exporters
        mock_html = MockHTML.return_value
        mock_docx = MockDOCX.return_value
        
        service = ExportService(export_config)
        
        summary = tmp_path / "summary.md"
        summary.write_text("content")
        
        service.export_unified_report(summary, [])
        
        # Should build unified markdown, convert to HTML, then DOCX
        mock_html.export.assert_called()
        mock_docx.export.assert_called()

    def test_remove_frontmatter(self, mock_exporters, export_config):
        """Test frontmatter removal logic via MarkdownProcessor."""
        from nibandha.export.application.helpers import MarkdownProcessor
        
        processor = MarkdownProcessor()
        content = "---\nkey: value\n---\nReal content"
        clean = processor.remove_frontmatter(content)
        assert clean == "Real content"
        
        content2 = "No frontmatter"
        clean2 = processor.remove_frontmatter(content2)
        assert clean2 == "No frontmatter"


    def test_load_metrics_cards(self, mock_exporters, export_config, tmp_path):
        """Test loading metrics cards from JSON sidecar via MetricsCardLoader."""
        from nibandha.export.application.helpers import MetricsCardLoader
        
        # Configure mapping in export_config
        export_config.metrics_mapping = {"unit_report": "unit"}
        loader = MetricsCardLoader(export_config)
        
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
        
        cards = loader.load_cards(detail_md)
        assert len(cards) == 1
        assert cards[0]['title'] == "Cov"

    def test_export_combined(self, mock_exporters, export_config, tmp_path):
        """Test export_combined concatenates multiple files."""
        _, _, MockDash = mock_exporters
        mock_dash = MockDash.return_value
        
        # Setup files in input dir
        input_dir = export_config.output_dir / "input"
        input_dir.mkdir()
        export_config.input_dir = input_dir
        
        (input_dir / "01_intro.md").write_text("# Intro")
        (input_dir / "02_body.md").write_text("# Body")
        
        service = ExportService(export_config)
        res = service.export_combined()
        
        mock_dash.export.assert_called_once()
        args, _ = mock_dash.export.call_args
        sections = args[0]
        assert len(sections) == 2
        
        # Checking generated filenames matching output logic (which returns mock generated paths or logic inside mock)
        # Because we mocked export methods returning paths:
        # Actually export_sections inside export_combined might just use the mocked dash logic.

