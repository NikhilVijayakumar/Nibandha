import pytest
from pathlib import Path
from unittest.mock import MagicMock
from nibandha.reporting.documentation.application.documentation_reporter import DocumentationReporter

class TestDocumentationPathResolution:
    
    @pytest.fixture
    def reporter(self, tmp_path):
        engine = MagicMock()
        viz = MagicMock()
        discovery = MagicMock()
        doc_paths = {}
        
        return DocumentationReporter(
            tmp_path / "out",
            tmp_path / "templates",
            doc_paths,
            engine,
            viz,
            discovery,
            tmp_path / "src"
        )
    
    def test_features_path_priority(self, reporter, tmp_path):
        """Verify features path is chosen if it exists."""
        module = "mymodule"
        
        # Setup features path
        features_dir = tmp_path / "docs" / "features" / module / "functional"
        features_dir.mkdir(parents=True)
        (features_dir / "README.md").touch()
        
        resolved = reporter._resolve_doc_path(tmp_path, module, "functional")
        assert resolved == features_dir
        
    def test_modules_fallback(self, reporter, tmp_path):
        """Verify modules path is fallback if features missing."""
        module = "oldmodule"
        
        # Setup modules path (only)
        modules_dir = tmp_path / "docs" / "modules" / module / "technical"
        modules_dir.mkdir(parents=True)
        
        resolved = reporter._resolve_doc_path(tmp_path, module, "technical")
        assert resolved == modules_dir
        
    def test_default_modules_if_neither_exist(self, reporter, tmp_path):
        """Verify modules path is returned default if neither exist."""
        module = "ghostmodule"
        
        resolved = reporter._resolve_doc_path(tmp_path, module, "test")
        expected = tmp_path / "docs" / "modules" / module / "test"
        assert resolved == expected

    def test_check_functional_finds_features(self, reporter, tmp_path):
        module = "featmod"
        
        # Setup code dir so check doesn't fail on timestamp
        (tmp_path / "src" / module).mkdir(parents=True)
        
        # Setup features doc
        doc_dir = tmp_path / "docs" / "features" / module / "functional"
        doc_dir.mkdir(parents=True)
        (doc_dir / "README.md").touch()
        
        result = reporter._check_functional(tmp_path, [module])
        assert result["modules"][module]["exists"] is True
