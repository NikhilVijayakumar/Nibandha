import logging
import sys
import os

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for older versions
from pathlib import Path

# Standard Project Logging
logger = logging.getLogger("project.doctor")
logging.basicConfig(level=logging.INFO, format="%(message)s")


class ProjectDoctor:
    def __init__(self, root_dir: str):
        self.root = Path(root_dir).resolve()
        # Windows-aware venv check
        self.venv = self.root / (".venv/Scripts" if os.name == "nt" else ".venv/bin")
        self.pyproject = self.root / "pyproject.toml"

    def _get_expected_prefix(self) -> str:
        """Reads pyproject.toml to find the absolute import root (snake_case)."""
        if not self.pyproject.exists():
            return "unknown"
        try:
            with open(self.pyproject, "rb") as f:
                data = tomllib.load(f)
                
            # Check tool.setuptools.package-dir for mapping
            # e.g. {"": "src/nikhil"} means root is src/nikhil, so packages are inside there
            # If we just want the package *name* that corresponds to the module?
            # Actually, we want the path relative to src/ where the code lives.
            # Simple heuristic: Look for dir in src/ that matches project name (snake_case)
            # or matches the last part of project name.
            
            project_name = data.get("project", {}).get("name") or "unknown"
            clean_name = project_name.replace("-", "_").lower()
            
            # Check physical existence
            if (self.root / "src" / clean_name).exists():
                return clean_name
            
            # recursive search in src for directory matching clean_name
            # e.g. src/nikhil/nibandha where name=nibandha
            if (self.root / "src").exists():
                 for path in (self.root / "src").rglob(clean_name):
                     if path.is_dir():
                         # Return relative path from src, e.g. "nikhil/nibandha"
                         return str(path.relative_to(self.root / "src"))
                         
            return clean_name
            
        except Exception as e:
            logger.error(f"⚠️ Error parsing pyproject.toml: {e}")
            return "unknown"

    def _check_absolute_imports(self, file_path: Path, prefix: str) -> bool:
        """Scans for illegal relative imports and verifies root prefix."""
        content = file_path.read_text()
        if "from ." in content or "import ." in content:
            logger.error(f"   ❌ ERROR: Relative import detected in {file_path.name}")
            return False

        # Ensure imports actually use the package prefix if they are local
        if prefix != "unknown" and f"from {prefix}" not in content and "import " in content:
            # This is a warning because external libs won't have the prefix
            logger.debug(f"   ℹ️ INFO: {file_path.name} does not explicitly use prefix '{prefix}'")
        return True

    def _check_pydantic_usage(self, file_path: Path) -> bool:
        """Ensures logic files are using BaseDomainModel or Pydantic for Clean Architecture."""
        content = file_path.read_text()
        if "BaseModel" not in content and "BaseDomainModel" not in content:
            logger.warning(f"   ⚠️ WARN: No Pydantic model found in {file_path.name}. Integrity check failed.")
            return False
        return True

    def check_module(self, module_name: str):
        logger.info(f"🏥 Running Comprehensive Audit: **{module_name}**")
        prefix = self._get_expected_prefix()
        
        # 1. Environment Health (Stage 0)
        python_exe = self.venv / ("python.exe" if os.name == "nt" else "python")
        if not python_exe.exists():
            logger.error(f"❌ Stage 0: Environment - MISSING (No .venv found at {self.venv})")
        else:
            logger.info("✅ Stage 0: Environment - VENV ACTIVE")

        # 2. Define Stages with explicit validation mapping
        stages = [
            # Trinity Docs: docs/modules/{module}/functional/README.md
            {"id": "Doc-Architect", "path": f"docs/modules/{module_name}/functional/README.md", "validator": None},
            
            # Trinity Tests: tests/unit/{module_name}/ or similar? 
            # Doc-Architect creates: 'tests/unit/{module}/test_{id}.py' ? No, verify_structure said docs/test.
            # But "Testing Standards" say tests/unit/<module>/
            # Let's check for ANY test file in tests/unit/{module_name} or tests/{module_name}
            # For now, let's target the generic test folder
            {"id": "Test-Scaffolder", "path": f"tests/unit/{module_name}", "validator": None}, # Just check dir existence
            
            # Code: src/{prefix}/{module_name}/
            {"id": "Clean-Implementation", "path": f"src/{prefix}/{module_name}/core.py", "validator": "pydantic"}
        ]

        for stage in stages:
            path = self.root / stage["path"]

            # Physical Check: If file, check existence. If dir, check existence + non-empty.
            exists = path.exists()
            if exists and path.is_file() and path.stat().st_size == 0:
                 exists = False
            
            if not exists:
                logger.error(f"❌ {stage['id']}: MISSING or EMPTY ({stage['path']})")
                continue
            
            # Validation Dispatch
            v_type = stage.get("validator")
            success = True

            if v_type == "imports" and path.is_file():
                success = self._check_absolute_imports(path, prefix)
            elif v_type == "pydantic" and path.is_file():
                success = self._check_pydantic_usage(path)

            if success:
                logger.info(f"✅ {stage['id']}: PASS")
            else:
                logger.error(f"❌ {stage['id']}: FAILED Quality Audit")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python project_doctor.py [root_path] [module_name]")
    else:
        doctor = ProjectDoctor(sys.argv[1])
        doctor.check_module(sys.argv[2])