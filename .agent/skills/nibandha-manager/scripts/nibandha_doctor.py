import os
import sys
import logging
from pathlib import Path

# Use the library-grade logger
logger = logging.getLogger("nibandha.doctor")
logging.basicConfig(level=logging.INFO, format="%(message)s")


class NibandhaDoctor:
    def __init__(self, root_dir: str):
        self.root = Path(root_dir)
        self.stages = [
            {"id": "Stage 1: Doc-Architect", "path": "docs/modules/{mod}/README.md"},
            {"id": "Stage 2: Test-Scaffolder", "path": "tests/{mod}/test_integration.py"},
            {"id": "Stage 3: Clean-Implementation", "path": "src/{mod}/core.py"}
        ]

    def check_module(self, module_name: str):
        logger.info(f"🏥 Examining Module: **{module_name}**")
        logger.info("-" * 40)

        all_passed = True
        for stage in self.stages:
            check_path = self.root / stage["path"].format(mod=module_name)

            if check_path.exists() and check_path.stat().st_size > 0:
                logger.info(f"✅ {stage['id']}: PASS")
            else:
                logger.info(f"❌ {stage['id']}: MISSING or EMPTY")
                logger.info(f"   👉 Suggested Action: Nibandha Manager, create {module_name}")
                all_passed = False

        logger.info("-" * 40)
        if all_passed:
            logger.info("🟢 Module is HEALTHY and Verified.")
        else:
            logger.info("🟡 Module is INCOMPLETE.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python nibandha_doctor.py [root_path] [module_name]")
    else:
        doctor = NibandhaDoctor(sys.argv[1])
        doctor.check_module(sys.argv[2])