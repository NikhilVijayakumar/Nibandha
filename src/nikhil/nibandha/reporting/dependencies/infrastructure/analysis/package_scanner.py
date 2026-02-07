"""
Package Dependency Analyzer.
"""

import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from packaging import version as pkg_version
import logging

logger = logging.getLogger("nibandha.reporting.analysis")

class PackageScanner:
    """Analyzes package dependencies and versions."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.pyproject_path = project_root / "pyproject.toml"
        
    def analyze(self) -> Dict[str, Any]:
        """Run full analysis."""
        installed = self.get_installed_packages()
        outdated = self.get_outdated_packages()
        declared = self.parse_pyproject_dependencies()
        unused = self.find_unused_dependencies()
        
        from nibandha.reporting.shared.constants import UPDATE_TYPE_MAJOR, UPDATE_TYPE_MINOR, UPDATE_TYPE_PATCH

        up_to_date = len(declared) - len(outdated)
        major_updates = sum(1 for p in outdated if p["update_type"] == UPDATE_TYPE_MAJOR)
        minor_updates = sum(1 for p in outdated if p["update_type"] == UPDATE_TYPE_MINOR)
        patch_updates = sum(1 for p in outdated if p["update_type"] == UPDATE_TYPE_PATCH)
        
        return {
            "installed_count": len(installed),
            "outdated_count": len(outdated),
            "up_to_date_count": up_to_date,
            "major_updates": major_updates,
            "minor_updates": minor_updates,
            "patch_updates": patch_updates,
            "declared_count": len(declared),
            "unused_count": len(unused),
            "outdated_packages": outdated,
            "unused_packages": unused,
            "installed_packages": installed
        }
        
    def get_installed_packages(self) -> Dict[str, str]:
        """Get all installed packages and their versions."""
        try:
            result = subprocess.run(
                ["pip", "list", "--format=json"],
                capture_output=True, text=True, check=False
            )
            if result.returncode != 0:
                logger.error(f"Error getting packages: {result.stderr}")
                return {}
            packages = json.loads(result.stdout)
            return {pkg["name"].lower(): pkg["version"] for pkg in packages}
        except Exception as e:
            logger.error(f"Failed to run pip list: {e}")
            return {}

    def get_outdated_packages(self) -> List[Dict[str, str]]:
        """Get packages that have updates available (only for declared dependencies)."""
        declared = self.parse_pyproject_dependencies()
        if not declared: return []
        
        installed = self.get_installed_packages()
        outdated = []
        
        for pkg_name in declared.keys():
            current_version = installed.get(pkg_name.lower())
            if not current_version: continue
            
            latest_version = self._get_latest_pypi_version(pkg_name)
            
            if latest_version and latest_version != current_version:
                update_type = self._classify_update(current_version, latest_version)
                outdated.append({
                    "name": pkg_name,
                    "version": current_version,
                    "latest_version": latest_version,
                    "update_type": update_type
                })
        return outdated

    def _get_latest_pypi_version(self, package_name: str) -> Optional[str]:
        try:
            from nibandha.reporting.shared.constants import PIP_TIMEOUT_SECONDS
            result = subprocess.run(
                ["pip", "index", "versions", package_name],
                capture_output=True, text=True, timeout=PIP_TIMEOUT_SECONDS
            )
            if result.returncode == 0:
                # Parse: "package (X.Y.Z)" or "Available versions: X.Y.Z, ..."
                lines = result.stdout.splitlines()
                for line in lines:
                    if "Available versions:" in line or package_name in line:
                         vers: List[str] = re.findall(r'\d+\.\d+(?:\.\d+)?(?:\.\w+)?', line)
                         if vers: return vers[0]
        except Exception:
            pass
        return None

    def _classify_update(self, current: str, latest: str) -> str:
        from nibandha.reporting.shared.constants import UPDATE_TYPE_MAJOR, UPDATE_TYPE_MINOR, UPDATE_TYPE_PATCH, UPDATE_TYPE_UNKNOWN
        try:
            curr_ver = pkg_version.parse(current)
            latest_ver = pkg_version.parse(latest)
            
            c_parts = str(curr_ver).split('.')
            l_parts = str(latest_ver).split('.')
            
            if len(c_parts) >= 1 and len(l_parts) >= 1:
                if c_parts[0] != l_parts[0]: return UPDATE_TYPE_MAJOR
                elif len(c_parts) >= 2 and len(l_parts) >= 2:
                    if c_parts[1] != l_parts[1]: return UPDATE_TYPE_MINOR
            return UPDATE_TYPE_PATCH
        except:
            return UPDATE_TYPE_UNKNOWN

    def parse_pyproject_dependencies(self) -> Dict[str, str]:
        if not self.pyproject_path.exists(): return {}
        try:
            content = self.pyproject_path.read_text(encoding="utf-8")
        except:
            return {}
        return self._parse_dependencies_from_content(content)

    def _parse_dependencies_from_content(self, content: str) -> Dict[str, str]:
        dependencies: Dict[str, str] = {}
        in_deps = False
        in_dev_deps = False
        
        for line in content.splitlines():
            stripped = line.strip()
            
            # State transitions
            if "dependencies = [" in stripped:
                in_deps = True
                # Check for inline content
                match = re.search(r'\[(.*)\]', stripped)
                if match and match.group(1).strip():
                     parts = match.group(1).split(",")
                     for p in parts:
                         self._add_dependency(dependencies, p)
                continue
            elif "optional-dependencies]" in stripped:
                in_deps = False; continue
            elif stripped.startswith("dev = ["):
                in_dev_deps = True; continue
            
            if (in_deps or in_dev_deps) and "]" in stripped:
                in_deps = False; in_dev_deps = False; continue
                
            # Content parsing
            if (in_deps or in_dev_deps) and stripped and not stripped.startswith("#"):
                self._add_dependency(dependencies, stripped)
                
        return dependencies

    def _add_dependency(self, dependencies: Dict[str, str], line: str) -> None:
        dep = line.strip(' ",')
        if not dep: return
        
        name = dep
        if "@" in dep: name = dep.split("@")[0].strip()
        elif "==" in dep: name = dep.split("==")[0].strip()
        elif ">=" in dep: name = dep.split(">=")[0].strip()
        elif "<" in dep: name = dep.split("<")[0].strip()
        
        dependencies[name.lower()] = "latest"

    def find_unused_dependencies(self) -> List[str]:
        declared = set(self.parse_pyproject_dependencies().keys())
        if not declared: return []
        
        imported = set()
        src_dir = self.project_root / "src"
        
        exclusions = {
            "__pycache__", ".venv", "venv", "env", "test", "tests",
            "build", "dist", ".git", ".idea", ".vscode", "node_modules", 
            "site-packages", ".tox"
        }
        
        if src_dir.exists():
            for py_file in src_dir.rglob("*.py"):
                if any(ex in py_file.parts for ex in exclusions): continue
                imported.update(self._extract_imports_from_file(py_file))
                
        exceptions = {
            "pytest", "pytest-cov", "black", "ruff", "mypy",
            "pytest-json-report", "import-linter", "pytest-asyncio",
            "httpx", "uvicorn", "setuptools", "wheel", "twine",
            "pandas", "seaborn", "matplotlib", "jinja2", "types-pyyaml"
        }
        
        unused = []
        for dep in declared:
            norm = dep.replace("-", "_")
            if dep not in exceptions and dep not in imported and norm not in imported:
                unused.append(dep)
        return unused

    def _extract_imports_from_file(self, file_path: Path) -> Set[str]:
        imports: Set[str] = set()
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                     line = line.strip()
                     if line.startswith("import "):
                         parts = line.split()
                         if len(parts) >= 2: imports.add(parts[1].split(".")[0].lower())
                     elif line.startswith("from "):
                         parts = line.split()
                         if len(parts) >= 2: imports.add(parts[1].split(".")[0].lower())
        except: pass
        return imports
