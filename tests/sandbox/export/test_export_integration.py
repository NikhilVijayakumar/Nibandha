
import pytest
import json
import os
from pathlib import Path
from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.unified_root.infrastructure.filesystem_binder import FileSystemBinder
from nibandha.export.application.export_service import ExportService
from nibandha.configuration.infrastructure.file_loader import FileConfigLoader

from tests.sandbox.export.utils import run_export_test

def test_export_full_cycle(sandbox_root, mock_pypandoc):
    """
    Integration Test: Complete AppConfig -> Binder -> Export workflow.
    """
    
    inputs = {
        "quality_report.md": "# Quality Report\n\nCode quality: Excellent\nCoverage: 95%",
        "security_scan.md": "# Security Scan\n\nNo vulnerabilities found."
    }
    
    expected = [
        "report.html",
        "report.docx"
    ]

    run_export_test(
        sandbox_path=sandbox_root,
        test_name="Export Full Cycle",
        description="Verify full export workflow from markdown input to HTML/DOCX output.",
        export_config={
            "formats": ["html", "docx"]
        },
        input_files=inputs,
        expected_files=expected
    )

