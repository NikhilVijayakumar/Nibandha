
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
        "quality_report.html",
        # "quality_report.docx", # Mock pypandoc might not actually generate file depending on implementation?
        # The original test checked for docx. Let's include it.
        # If mock_pypandoc is a fixture that patches subprocess, it might not create files unless handled.
        # Let's assume for now we just want to match original expectations.
        "quality_report.docx",
        "security_scan.html",
        "security_scan.docx"
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

