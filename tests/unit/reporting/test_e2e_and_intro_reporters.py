
import pytest
from unittest.mock import MagicMock, patch, ANY
from pathlib import Path
import datetime

from nibandha.reporting.e2e.application.e2e_reporter import E2EReporter
from nibandha.reporting.introduction.application.introduction_reporter import IntroductionReporter

class TestE2EReporter:
    
    @pytest.fixture
    def reporter(self, tmp_path):
        engine = MagicMock()
        viz = MagicMock()
        collector = MagicMock()
        return E2EReporter(
            tmp_path / "out",
            tmp_path / "templates",
            tmp_path / "docs", # doc_root
            engine,
            viz,
            collector 
        )

    def test_generate_happy_path(self, reporter):
        """RPT-E2E-001: Happy Path Generation."""
        # Mock pytest E2E data
        data = {
            "tests": [
                {"nodeid": "tests/e2e/test_login.py::test_valid_login", "outcome": "passed", "call": {"duration": 1.0}},
                {"nodeid": "tests/e2e/test_checkout.py::test_cart", "outcome": "passed", "call": {"duration": 2.0}}
            ],
            "summary": {"passed": 2, "total": 2} # Optional depending on builder
        }
        timestamp = "2023-01-01"
        
        reporter.template_engine.render.return_value = "<html>"
        
        result = reporter.generate(data, timestamp, "Proj")
        
        assert result["passed"] == 2
        assert result["pass_rate"] == 100.0
        assert result["grade"] == "A"
        
        reporter.viz_provider.generate_e2e_test_charts.assert_called()
        reporter.template_engine.render.assert_called()

    def test_generate_partial_failure(self, reporter):
        """RPT-E2E-002: Handle failures."""
        data = {
            "tests": [
                {"nodeid": "tests/e2e/test_a.py", "outcome": "passed", "call": {"duration": 1.0}},
                {"nodeid": "tests/e2e/test_b.py", "outcome": "failed", "call": {"duration": 1.0}}
            ]
        }
        result = reporter.generate(data, "ts", "Proj")
        
        assert result["passed"] == 1
        assert result["failed"] == 1
        assert result["pass_rate"] == 50.0
        assert result["grade"] == "F" 

    def test_enrichment_logic(self, reporter):
        """Verify internal enrichment logic matches expectations."""
        # This test ensures internal data structure is correct
        data = {"tests": [{"nodeid": "tests/e2e/auth/test_login.py::test_a", "outcome": "passed"}]}
        
        res = reporter.generate(data, "ts", "Proj")
        
        # E2EReporter flattens modules into detailed_sections string
        assert "detailed_sections" in res
        assert "Auth" in res["detailed_sections"]


class TestIntroductionReporter:
    
    def test_generate(self, tmp_path):
        """RPT-INT-001: Verify introduction output."""
        engine = MagicMock()
        intro = IntroductionReporter(tmp_path, tmp_path / "tpl", engine)
        
        intro.generate("MyProject")
        
        engine.render.assert_called_with(
            "introduction_template.md",
            {"project_name": "MyProject"},
            ANY
        )
