import pytest
from nikhil.nibandha.reporting.e2e.application.e2e_reporter import E2EReporter
from pathlib import Path

class TestE2EReporterFix:
    def test_resolve_test_module_with_integration_pattern(self):
        """Verify that _resolve_test_module properly handles test_{module}_integration.py pattern."""
        reporter = E2EReporter(
            output_dir=Path("tmp"),
            templates_dir=Path("tmp"),
            docs_dir=Path("tmp")
        )
        
        # Test case mirroring the bug report
        test_item = {
            "nodeid": "tests/integration/test_semantic_integration.py::test_workflow"
        }
        
        module_name = reporter._resolve_test_module(test_item)
        assert module_name == "Semantic", f"Expected 'Semantic', got '{module_name}'"

    def test_resolve_test_module_legacy_fallback(self):
        """Ensure legacy paths still work."""
        reporter = E2EReporter(
            output_dir=Path("tmp"),
            templates_dir=Path("tmp"),
            docs_dir=Path("tmp")
        )
        
        test_item = {
            "nodeid": "tests/e2e/auth/test_login.py::test_login_success"
        }
        
        module_name = reporter._resolve_test_module(test_item)
        assert module_name == "Auth"
