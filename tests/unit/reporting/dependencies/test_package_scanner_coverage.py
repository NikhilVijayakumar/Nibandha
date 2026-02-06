
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json
from nibandha.reporting.dependencies.infrastructure.analysis.package_scanner import PackageScanner

@pytest.fixture
def mock_subprocess():
    with patch("subprocess.run") as mock_run:
        yield mock_run

@pytest.fixture
def scanner(tmp_path):
    return PackageScanner(tmp_path)

def test_get_installed_packages_success(scanner, mock_subprocess):
    mock_subprocess.return_value.returncode = 0
    mock_subprocess.return_value.stdout = json.dumps([
        {"name": "PackageA", "version": "1.0.0"},
        {"name": "PackageB", "version": "2.1.0"}
    ])
    
    packages = scanner.get_installed_packages()
    assert packages["packagea"] == "1.0.0"
    assert packages["packageb"] == "2.1.0"

def test_get_installed_packages_fail(scanner, mock_subprocess):
    mock_subprocess.return_value.returncode = 1
    mock_subprocess.return_value.stderr = "Error"
    assert scanner.get_installed_packages() == {}

def test_get_latest_pypi_version(scanner, mock_subprocess):
    mock_subprocess.return_value.returncode = 0
    mock_subprocess.return_value.stdout = "package (2.0.0)\nAvailable versions: 2.0.0, 1.0.0"
    
    ver = scanner._get_latest_pypi_version("package")
    assert ver == "2.0.0"

def test_classify_update(scanner):
    assert scanner._classify_update("1.0.0", "2.0.0") == "MAJOR"
    assert scanner._classify_update("1.1.0", "1.2.0") == "MINOR"
    assert scanner._classify_update("1.1.1", "1.1.2") == "PATCH"
    assert scanner._classify_update("1.0.0", "1.0.0") == "PATCH" # Should conceptually be NONE but logic falls through to Patch if not major/minor
    # Logic: c[0]!=l[0] -> Major; c[1]!=l[1] -> Minor; else Patch.
    # If equal, it returns Patch which is slightly weird but safe for update detection (updates only trigger if ver != ver)
    
def test_parse_pyproject_dependencies(scanner, tmp_path):
    content = """
    [project]
    dependencies = [
        "requests>=2.0.0", 
        "numpy==1.0",
        "pandas"
    ]
    
    [tool.x]
    dev = [
        "pytest", 
        "black"
    ]
    """
    (tmp_path / "pyproject.toml").write_text(content, encoding="utf-8")
    
    deps = scanner.parse_pyproject_dependencies()
    assert "requests" in deps
    assert "numpy" in deps
    assert "pandas" in deps
    assert "pytest" in deps
    assert "black" in deps

def test_find_unused_dependencies(scanner, tmp_path, mock_subprocess):
    # Setup Pyproject
    (tmp_path / "pyproject.toml").write_text("""
    dependencies = ["used-pkg", "unused-pkg"]
    """, encoding="utf-8")
    
    # Setup Src
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text("import used_pkg\nimport sys", encoding="utf-8")
    (src / "ignored.py").write_text("import nothing", encoding="utf-8")
    
    unused = scanner.find_unused_dependencies()
    assert "unused-pkg" in unused
    assert "used-pkg" not in unused

def test_analyze(scanner, mock_subprocess):
    # Mock installed
    mock_subprocess.return_value.returncode = 0
    mock_subprocess.return_value.stdout = json.dumps([{"name": "pkg", "version": "1.0"}])
    
    # Mock pyproject
    (scanner.project_root / "pyproject.toml").write_text('dependencies = ["pkg"]', encoding="utf-8")
    
    # Allow _get_latest to fail/return None safely (or mock it)
    with patch.object(scanner, "_get_latest_pypi_version", return_value="1.0"):
        res = scanner.analyze()
        assert res["installed_count"] == 1
        assert res["declared_count"] == 1

def test_parse_inline_deps(scanner):
    content = 'dependencies = ["a", "b"]'
    deps = scanner._parse_dependencies_from_content(content)
    assert "a" in deps
    assert "b" in deps

def test_extract_imports(scanner, tmp_path):
    f = tmp_path / "test.py"
    f.write_text("from foo import bar\nimport baz.qux", encoding="utf-8")
    imports = scanner._extract_imports_from_file(f)
    assert "foo" in imports
    assert "baz" in imports
