
import pytest
from pathlib import Path
from nibandha.reporting import ReportGenerator
from nibandha.reporting.dependencies.application.dependency_reporter import DependencyReporter
from nibandha.reporting.dependencies.application.package_reporter import PackageReporter

def test_rpt_unit_001_initialization(tmp_path):
    """RPT-UNIT-001: Verify generator initializes with defaults."""
    out_dir = tmp_path / "reports"
    gen = ReportGenerator(output_dir=str(out_dir))
    
    assert gen.output_dir == out_dir.resolve()
    assert gen.templates_dir.name == "templates"
    assert gen.templates_dir.exists()

def test_rpt_unit_003_reporter_instantiation(tmp_path):
    """RPT-UNIT-003: Verify all sub-reporters are initialized."""
    gen = ReportGenerator(output_dir=str(tmp_path))
    
    assert gen.unit_reporter is not None
    assert gen.e2e_reporter is not None
    assert gen.quality_reporter is not None
    assert isinstance(gen.dep_reporter, DependencyReporter)
    assert isinstance(gen.pkg_reporter, PackageReporter)
