
import pytest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path

# Correct imports based on file exploration
from nibandha.reporting.dependencies.infrastructure.analysis.package_scanner import PackageScanner
from nibandha.reporting.dependencies.infrastructure.analysis.module_scanner import ModuleScanner
from nibandha.reporting.dependencies.application.dependency_reporter import DependencyReporter

class TestPackageScanner:
    

    def test_scan_pyproject_success(self, tmp_path):
        """RPT-DP-001: Scan valid pyproject.toml."""
        scanner = PackageScanner(tmp_path)
        
        # Create dummy pyproject.toml
        toml_content = """
        [project]
        dependencies = [ "requests>=2.0" ]
        """
        (tmp_path / "pyproject.toml").write_text(toml_content)
        
        with patch.object(scanner, "get_installed_packages", return_value={"requests": "2.0.0"}), \
             patch.object(scanner, "get_outdated_packages", return_value=[]), \
             patch.object(scanner, "find_unused_dependencies", return_value=[]):
             
             # The parse_pyproject_dependencies will read the file we wrote
             res = scanner.analyze()
             
             assert res["declared_count"] == 1
             assert res["installed_count"] == 1
             assert res["outdated_count"] == 0
            
    def test_scan_missing_file(self, tmp_path):
        """RPT-DP-001: Handle missing pyproject."""
        scanner = PackageScanner(tmp_path)
        # Ensure file doesn't exist
        if (tmp_path / "pyproject.toml").exists():
            (tmp_path / "pyproject.toml").unlink()
            
        res = scanner.analyze()
        assert res["declared_count"] == 0


class TestModuleScanner:
    
    def test_circular_detection(self, tmp_path):
        """RPT-DP-003: Verify circular reference detection."""
        scanner = ModuleScanner(tmp_path)
        
        # Inject graph directly to test finding logic
        scanner.dependencies = {
            "A": ["B"],
            "B": ["A"],
            "C": []
        }
        
        cycles = scanner.find_circular_dependencies()
        assert len(cycles) > 0
        cycle_names = [{a, b} for a, b in cycles]
        assert {"A", "B"} in cycle_names


class TestDependencyReporter:
    
    @pytest.fixture
    def reporter(self, tmp_path):
        return DependencyReporter(tmp_path, MagicMock(), MagicMock())
        
    def test_calculate_grades(self, reporter):
        """RPT-DP-002: Verify module grading logic based on Fan-Out."""
        deps = {
            "Clean": ["A", "B"], # FanOut 2 -> A
            "Busy": ["A", "B", "C", "D", "E"], # FanOut 5 -> B
            "Messy": ["A", "B", "C", "D", "E", "F", "G", "H", "I"], # FanOut 9 -> C
            "Cycle": ["Clean"]
        }
        circular = [("Cycle", "Cycle")] # Self-reference to keep Clean innocent
        
        grades = reporter._calculate_module_grades(deps, circular)
        
        grade_map = {g["name"]: g["grade"] for g in grades}
        
        assert grade_map["Clean"] == "A"
        assert grade_map["Busy"] == "B"
        assert grade_map["Messy"] == "C"
        assert grade_map["Cycle"] == "F"
