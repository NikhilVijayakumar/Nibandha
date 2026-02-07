
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from nibandha.reporting.dependencies.infrastructure.analysis.package_scanner import PackageScanner
from nibandha.reporting.dependencies.application.dependency_reporter import DependencyReporter

class TestPackageScannerEdges:
    
    @pytest.fixture
    def empty_root(self, tmp_path):
        return tmp_path
    
    def test_scanner_no_pyproject(self, empty_root):
        """Test scanning without pyproject.toml returns empty dicts."""
        scanner = PackageScanner(empty_root)
        deps = scanner.parse_pyproject_dependencies()
        assert deps == {}
        
    def test_scanner_malformed_pyproject(self, empty_root):
        """Test scanning with malformed file handles error gracefully."""
        p = empty_root / "pyproject.toml"
        p.write_text("not a toml file", encoding="utf-8")
        scanner = PackageScanner(empty_root)
        # Should catch exception and return empty or partial
        # Based on implementation, it splits lines.
        deps = scanner.parse_pyproject_dependencies()
        assert deps == {}
        
    def test_scanner_parsing_logic(self, empty_root):
        """Test the split logic for sections."""
        p = empty_root / "pyproject.toml"
        content = """
        [project]
        dependencies = [
            "foo>=1.0",
            "bar==2.0",
            "baz"
        ]
        
        [context]
        optional-dependencies]
        dev = ["ignored"]
        """
        p.write_text(content, encoding="utf-8")
        scanner = PackageScanner(empty_root)
        deps = scanner.parse_pyproject_dependencies()
        assert "foo" in deps
        assert "bar" in deps
        assert "baz" in deps

class TestDependencyReporterEdges:
    
    @pytest.fixture
    def reporter(self, tmp_path):
        return DependencyReporter(tmp_path, tmp_path / "templates")
        
    @patch("nibandha.reporting.dependencies.application.dependency_reporter.ModuleScanner")
    def test_generate_handles_empty_scan(self, mock_scanner, reporter, tmp_path):
        """Test generation flow when scan returns no dependencies."""
        mock_scanner.return_value.scan.return_value = {}
        mock_scanner.return_value.find_circular_dependencies.return_value = []
        mock_scanner.return_value.get_most_imported.return_value = []
        mock_scanner.return_value.get_most_dependent.return_value = []
        mock_scanner.return_value.get_isolated_modules.return_value = []
        
        # Mock template engine to avoid rendering
        reporter.template_engine = MagicMock()
        
        res = reporter.generate(tmp_path / "src")
        
        assert res["total_modules"] == 0
        assert res["status"] == "PASS"
        # mock_viz assertion removed as we removed the patch
        # mock_viz.plot_dependency_graph.assert_called()
