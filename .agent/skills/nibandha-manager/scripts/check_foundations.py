import sys
import logging
from pathlib import Path

logger = logging.getLogger("sentinel.validator")


def is_stage_complete(stage: str, required_files: list) -> bool:
    """Checks if all required artifacts exist and are non-empty."""
    for f in required_files:
        path = Path(f)
        if not path.exists() or path.stat().st_size == 0:
            return False
    return True


if __name__ == "__main__":
    stage_name = sys.argv[1]
    files_to_check = sys.argv[2:]

    if is_stage_complete(stage_name, files_to_check):
        # Exit with a special code (e.g., 0 for success/skip)
        logger.info(f"⏭️ Skipping {stage_name}: Artifacts already verified.")
        sys.exit(0)
    else:
        # Exit with code 2 to indicate "Work Needed"
        logger.info(f"🔧 Starting {stage_name}: Artifacts missing or incomplete.")
        sys.exit(2)