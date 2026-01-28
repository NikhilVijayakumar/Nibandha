
import pytest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
import ast

from nibandha.reporting.dependencies.infrastructure.analysis.module_scanner import ModuleScanner
from nibandha.reporting.shared.data.data_builders import UnitDataBuilder

class TestModuleScannerDeep:
    
    def test_extract_imports_ast_logic(self, tmp_path):
        """Verify AST parsing for internal package imports."""
        scanner = ModuleScanner(tmp_path, package_roots=['nikhil.nibandha'])
        
        code = """
import os # Standard lib (ignored)
import nikhil.nibandha.logging.adapters # Internal -> Logging
from nikhil.nibandha.export import service # Internal -> Export
from other.package import stuff # External (ignored)
from nikhil.nibandha import root_thing # Root (ignored logic?)
        """
        
        f = tmp_path / "test_file.py"
        f.write_text(code)
        
        imports = scanner._extract_imports(f)
        
        # internal logic: splits by root, takes next part capialized
        # nikhil.nibandha.logging... -> Logging
        # nikhil.nibandha.export... -> Export
        
        assert "Logging" in imports
        assert "Export" in imports
        assert "Os" not in imports 

    def test_extract_imports_read_error(self, tmp_path):
        """Verify handling of file read errors."""
        scanner = ModuleScanner(tmp_path)
        f = tmp_path / "bad_file.py"
        f.touch()
        
        # Mock open to raise exception
        with patch("builtins.open", side_effect=PermissionError):
            imports = scanner._extract_imports(f)
            assert imports == set()

    def test_get_module_name_edge_cases(self, tmp_path):
        scanner = ModuleScanner(tmp_path)
        
        # Test file directly in root
        f = tmp_path / "root_script.py"
        name = scanner._get_module_name(f)
        assert name == "Root_script" or name == "Root" # implementation dependent
        
        # Test __init__
        f2 = tmp_path / "sub" / "__init__.py"
        name2 = scanner._get_module_name(f2)
        assert name2 == "Sub"

class TestUnitDataBuilderDeep:
    
    def test_grading_thresholds(self):
        """Verify explicit grading boundaries."""
        builder = UnitDataBuilder()
        
        # Helper to create coverage data structure
        def make_cov(percent):
             return {"summary": {"num_statements": 100, "covered_lines": percent, "missing_lines": 100-percent}}
        
        files = {
            "src/nikhil/nibandha/ModuleA/a.py": make_cov(80), # A
            "src/nikhil/nibandha/ModuleB/b.py": make_cov(70), # B
            "src/nikhil/nibandha/ModuleC/c.py": make_cov(50), # C
            "src/nikhil/nibandha/ModuleD/d.py": make_cov(30), # D
            "src/nikhil/nibandha/ModuleE/e.py": make_cov(29), # F
        }
        
        pytest_data = {}
        cov_data = {"files": files}
        
        breakdown = builder._build_module_breakdown(pytest_data, cov_data)
        
        grades = {m["name"]: m["grade"] for m in breakdown}
        assert grades["Modulea"] == "A"
        assert grades["Moduleb"] == "B"
        assert grades["Modulec"] == "C"
        assert grades["Moduled"] == "D"
        assert grades["Modulee"] == "F"

    def test_weird_paths(self):
        """Verify path parsing for non-standard paths."""
        builder = UnitDataBuilder()
        files = {
             # Path without src/nikhil/nibandha prefix - should be skipped or handled?
             "/tmp/random/file.py": {"summary": {}},
             # Fallback path logic
             "src/nikhil/nibandha/MyMod/f.py": {"summary": {"num_statements": 1}}
        }
        breakdown = builder._build_module_breakdown({}, {"files": files})
        
        names = [m["name"] for m in breakdown]
        assert "Mymod" in names
        assert "Random" not in names # Should likely be skipped by logic

    def test_extract_failures_crash_data(self):
        """Verify crash data extraction."""
        builder = UnitDataBuilder()
        data = {
            "tests": [
                {
                    "nodeid": "test_crash", 
                    "outcome": "failed", 
                    "call": {"crash": {"message": "Boom"}, "longrepr": "Traceback..."}
                }
            ]
        }
        failures = builder._extract_failures(data)
        assert failures[0]["error"] == "Boom"
        assert failures[0]["traceback"] == "Traceback..."
