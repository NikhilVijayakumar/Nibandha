
import pytest
from unittest.mock import MagicMock, patch, ANY
from pathlib import Path
import time
import datetime
from nibandha.reporting.documentation.application.documentation_reporter import DocumentationReporter
from nibandha.reporting.shared.infrastructure import utils

@pytest.fixture
def reporter(tmp_path):
    engine = MagicMock()
    viz = MagicMock()
    discovery = MagicMock()
    
    # Setup project structure
    project_root = tmp_path
    
    return DocumentationReporter(
        output_dir=tmp_path / "out",
        templates_dir=tmp_path / "templates",
        doc_paths={}, # Not really used by logic relying on _resolve_doc_path
        template_engine=engine,
        viz_provider=viz,
        module_discovery=discovery,
        source_root=tmp_path / "src"
    )

def test_resolve_doc_path_precedence(reporter, tmp_path):
    root = tmp_path
    mod = "mymod"
    cat = "functional"
    
    feat = root / "docs" / "features" / mod / cat
    feat.mkdir(parents=True)
    
    resolved = reporter._resolve_doc_path(root, mod, cat)
    assert resolved == feat
    
    # Test fallback by using a module that only exists in 'modules'
    # We don't need to delete features dir, just use a mod name that isn't in features
    mod2 = "legacy"
    mod_legacy = root / "docs" / "modules" / mod2 / cat
    mod_legacy.mkdir(parents=True)
    
    resolved2 = reporter._resolve_doc_path(root, mod2, cat)
    assert resolved2 == mod_legacy

def test_check_functional(reporter, tmp_path):
    root = tmp_path
    mod = "mod_a"
    
    # Create Source (for timestamp)
    src_mod = tmp_path / "src" / mod 
    src_mod.mkdir(parents=True)
    (src_mod / "code.py").touch()
    
    # Create Doc
    doc_dir = root / "docs" / "features" / mod / "functional"
    doc_dir.mkdir(parents=True)
    (doc_dir / "README.md").touch()
    
    # Force timestamps
    now = time.time()
    os.utime(src_mod / "code.py", (now - 100, now - 100))
    os.utime(doc_dir / "README.md", (now, now)) # Doc newer
    
    res = reporter._check_functional(root, [mod])
    
    assert res["stats"]["documented"] == 1
    assert res["modules"][mod]["exists"] == True
    assert res["modules"][mod]["drift"] == 0

def test_check_technical_missing(reporter, tmp_path):
    res = reporter._check_technical(tmp_path, ["missing_mod"])
    assert res["stats"]["documented"] == 0
    assert res["stats"]["missing"] == 1
    assert res["modules"]["missing_mod"]["exists"] == False

def test_check_test_coverage(reporter, tmp_path):
    root = tmp_path
    mod = "mod_test"
    
    # Source
    (tmp_path / "src" / mod).mkdir(parents=True)
    
    # Doc
    doc_dir = root / "docs" / "features" / mod / "test"
    doc_dir.mkdir(parents=True)
    (doc_dir / "unit_scenarios.md").touch() # Alt name check
    
    res = reporter._check_test(root, [mod])
    
    assert res["modules"][mod]["unit_exists"] == True
    assert res["modules"][mod]["e2e_exists"] == False
    assert res["stats"]["documented"] == 1 

def test_render_report_logic(reporter):
    # Prepare data structure matching output of checks
    data = {
        "functional": {
            "stats": {"documented": 10, "missing": 0},
            "modules": {"ModA": {"exists": True, "drift": 0}}
        },
        "technical": {
            "stats": {"documented": 5, "missing": 5},
            "modules": {"ModA": {"exists": False, "drift": -1}}
        },
        "test": {
            "stats": {"documented": 8, "missing": 2},
            "modules": {"ModA": {"unit_exists": True, "e2e_exists": True, "max_drift": 0}}
        }
    }
    charts = {"doc_coverage": "/path/to/cov.png"}
    
    reporter._render_report(data, charts, "TestProject")
    
    # Check render call context
    reporter.template_engine.render.assert_called()
    args, kwargs = reporter.template_engine.render.call_args
    ctx = args[1]
    
    # Verify Context content
    assert ctx["func_coverage"] == "100.0"
    assert ctx["tech_coverage"] == "50.0"
    assert ctx["test_coverage"] == "80.0"
    assert "ModA" in ctx["func_table"]
    assert "ModA" in ctx["test_table"]
    
    # Verify Grade Colors
    assert ctx["func_grade"] == "A"
    assert ctx["tech_grade"] == "F" # 50%

import os
