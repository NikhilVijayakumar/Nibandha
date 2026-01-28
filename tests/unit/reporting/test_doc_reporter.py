
import pytest
from unittest.mock import MagicMock, patch, ANY
from pathlib import Path
import datetime
import time
import os

from nibandha.reporting.documentation.application.documentation_reporter import DocumentationReporter

class TestDocumentationReporter:
    
    @pytest.fixture
    def reporter(self, tmp_path):
        engine = MagicMock()
        viz = MagicMock()
        discovery = MagicMock()
        
        # Mock doc paths
        doc_paths = {
            "functional": tmp_path / "docs/functional",
            "technical": tmp_path / "docs/technical",
            "test": tmp_path / "docs/test",
            "e2e": tmp_path / "docs/e2e"
        }
        
        return DocumentationReporter(
            tmp_path / "out",
            tmp_path / "templates",
            doc_paths,
            engine,
            viz,
            discovery,
            tmp_path / "src"
        )
        
    def test_drift_calculation_logic(self, reporter):
        """RPT-DOC-002: Verify drift logic."""
        now = time.time()
        day = 86400
        
        # Doc is 10 days older than code
        doc_ts = now - (20 * day)
        code_ts = now - (10 * day)
        
        drift = reporter._calc_drift_days(doc_ts, code_ts)
        assert drift in [9, 10, 11] # Allow small floating point variation
        
        # Doc is newer than code -> 0 drift
        doc_ts_new = now
        drift_clean = reporter._calc_drift_days(doc_ts_new, code_ts)
        assert drift_clean == 0

    def test_generate_integration(self, reporter):
        """RPT-DOC-003: Verify orchestration."""
        with patch.object(reporter, "_check_functional") as mock_func, \
             patch.object(reporter, "_check_technical") as mock_tech, \
             patch.object(reporter, "_check_test") as mock_test:
             
             # Fixed: returned stats include documented/missing
             mock_func.return_value = {"stats": {"grade": "A", "documented": 1, "missing": 0}, "modules": {}}
             mock_tech.return_value = {"stats": {"grade": "B", "documented": 1, "missing": 0}, "modules": {}}
             mock_test.return_value = {"stats": {"grade": "C", "documented": 1, "missing": 0}, "modules": {}}
             
             reporter.generate(Path("."))
             
             reporter.template_engine.render.assert_called()
             reporter.viz_provider.generate_documentation_charts.assert_called()

    def test_timestamp_utils(self, reporter, tmp_path):
        """Test timestamp helpers."""
        d = tmp_path / "test_dir"
        d.mkdir()
        (d / "file.txt").touch()
        
        # Should work on directory
        ts = reporter._get_dir_timestamp(d)
        assert ts > 0
        
        # Code timestamp
        ts_code = reporter._get_code_timestamp(tmp_path, "unknown_module")
        assert ts_code > 0 # Fallback to now() if not found
