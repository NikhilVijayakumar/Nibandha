import sys
import logging
import os
from pathlib import Path

# Identity Alignment: Changed from sentinel to project.chatha
logger = logging.getLogger("project.chatha.validator")
logging.basicConfig(level=logging.INFO, format='%(message)s')


def verify_environment() -> bool:
    """Rule: Always use the local virtual environment at ./.venv"""
    # Check for Windows first based on your E:\ pathing, then fallback to Linux
    venv_python_win = Path("./.venv/Scripts/python.exe")
    venv_python_unix = Path("./.venv/bin/python")

    executable = venv_python_win if os.name == 'nt' else venv_python_unix

    if not executable.exists():
        logger.error(f"❌ CRITICAL: Environment Violation. {executable} not found.")
        logger.error("👉 Required: python -m venv .venv && .venv/Scripts/pip install -e .")
        return False
    return True


def get_package_root() -> str:
    """Rule: Discovery via pyproject.toml name field."""
    pyproject = Path("pyproject.toml")
    if not pyproject.exists():
        logger.warning("⚠️ pyproject.toml missing. Cannot verify Absolute Import Root.")
        return "unknown"

    content = pyproject.read_text()
    for line in content.splitlines():
        if line.strip().startswith("name ="):
            # Clean 'name = "my-project"' -> 'my_project'
            raw_name = line.split("=")[-1].strip().replace('"', '').replace("'", "")
            return raw_name.replace("-", "_")
    return "unknown"


def is_stage_complete(stage: str, required_files: list, root: str) -> bool:
    """Checks for artifact existence, size, and absolute import compliance."""
    for f in required_files:
        # Handle path placeholders if the manager passes them raw
        actual_file = f.replace("{root}", root)
        path = Path(actual_file)

        if not path.exists():
            logger.info(f"  [MISSING] {actual_file}")
            return False
        if path.stat().st_size == 0:
            logger.info(f"  [EMPTY] {actual_file}")
            return False

        # Rule: Absolute Import Enforcement
        if path.suffix == ".py":
            code = path.read_text()
            if "from ." in code or "import ." in code:
                logger.error(f"❌ Violation: Relative import detected in {actual_file}")
                return False
            # Check if it uses the discovered root for absolute imports
            if root != "unknown" and f"from {root}" not in code and "import " in code:
                # We log a warning but don't fail unless relative imports are used
                logger.debug(f"ℹ️ Note: {actual_file} may not be using absolute root '{root}'")

    return True


if __name__ == "__main__":
    if len(sys.argv) < 3:
        logger.error("Usage: check_foundations.py <stage_name> <file1> <file2> ...")
        sys.exit(1)

    stage_name = sys.argv[1]
    files_to_check = sys.argv[2:]

    # 1. Environment Gate (Stage 0)
    if not verify_environment():
        sys.exit(1)

    # 2. Package Discovery
    root_dir = get_package_root()
    logger.info(f"🌍 Environment Verified | Root: {root_dir} | Stage: {stage_name}")

    # 3. Artifact Gate
    if is_stage_complete(stage_name, files_to_check, root_dir):
        logger.info(f"⏭️  SKIP: Stage '{stage_name}' artifacts verified.")
        sys.exit(0)
    else:
        logger.info(f"🔧 TRIGGER: Stage '{stage_name}' requires attention.")
        sys.exit(2)