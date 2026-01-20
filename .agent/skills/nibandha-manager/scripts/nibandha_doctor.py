import logging
import sys
import os

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for older versions
from pathlib import Path

# Standard Nibandha Logging
logger = logging.getLogger("nibandha.doctor")
logging.basicConfig(level=logging.INFO, format="%(message)s")


class NibandhaDoctor:
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
                # Check for 'project.name' or 'tool.poetry.name'
                name = data.get("project", {}).get("name") or data.get("tool", {}).get("poetry", {}).get("name",
                                                                                                         "unknown")
                return name.replace("-", "_")
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
        # Check for python.exe/python binary existence
        python_exe = self.venv / ("python.exe" if os.name == "nt" else "python")
        if not python_exe.exists():
            logger.error(f"❌ Stage 0: Environment - MISSING (No .venv found at {self.venv})")
        else:
            logger.info("✅ Stage 0: Environment - VENV ACTIVE")

        # 2. Define Stages with explicit validation mapping
        # Note: Pathing follows E:\Python\Nibandha\src\{prefix}\{module}\core.py
        stages = [
            {"id": "Doc-Architect", "path": f"docs/modules/{module_name}/README.md", "validator": None},
            {"id": "Test-Scaffolder", "path": f"tests/{module_name}/test_unit.py", "validator": "imports"},
            {"id": "Clean-Implementation", "path": f"src/{prefix}/{module_name}/core.py", "validator": "pydantic"}
        ]

        for stage in stages:
            path = self.root / stage["path"]

            # Physical Check
            if not path.exists() or path.stat().st_size == 0:
                logger.error(f"❌ {stage['id']}: MISSING or EMPTY ({stage['path']})")
                continue

            # Validation Dispatch
            v_type = stage["validator"]
            success = True

            if v_type == "imports":
                success = self._check_absolute_imports(path, prefix)
            elif v_type == "pydantic":
                success = self._check_pydantic_usage(path)

            if success:
                logger.info(f"✅ {stage['id']}: PASS")
            else:
                logger.error(f"❌ {stage['id']}: FAILED Quality Audit")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python nibandha_doctor.py [root_path] [module_name]")
    else:
        doctor = NibandhaDoctor(sys.argv[1])
        doctor.check_module(sys.argv[2])