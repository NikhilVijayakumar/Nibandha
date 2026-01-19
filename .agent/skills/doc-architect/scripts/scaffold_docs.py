import os
import sys
import logging
from pathlib import Path

# Configure library-grade logger
logger = logging.getLogger("nibandha.scaffolder")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


def inject_template(path: Path, title: str, is_test: bool = False):
    """Injects platform-agnostic boilerplate into new files."""
    if path.exists():
        return

    if is_test:
        content = f"# Test Scenarios: {title}\n\n| ID | Scenario | Category | Expected |\n|:---|:---|:---|:---|\n"
    else:
        content = f"# Component Spec: {title}\n\n## Role\n\n## Data Schema (Contract)\n| Attribute | Type | Req | Constraints |\n|:---|:---|:---|:---|\n"

    path.write_text(content)


def create_nibandha_docs(root_path: str, module_name: str, sub_modules: list):
    root = Path(root_path)
    logger.info("🏗️ Building Platform-Agnostic Blueprint for: **%s**", module_name)

    # 1. Functional Specs (docs/modules/)
    docs_modules = root / "docs" / "modules" / module_name
    docs_modules.mkdir(parents=True, exist_ok=True)

    inject_template(docs_modules / "README.md", f"{module_name} Overview")

    for sub in sub_modules:
        inject_template(docs_modules / f"{sub}.md", sub)
        logger.info("Generated spec: %s", sub)

    # 2. Test Scenarios (docs/test/)
    docs_test = root / "docs" / "test" / module_name
    docs_test.mkdir(parents=True, exist_ok=True)

    # Always ensure an integration point exists
    targets = list(dict.fromkeys(sub_modules + ["integration"]))

    for comp in targets:
        inject_template(docs_test / f"{comp}_scenarios.md", comp, is_test=True)
        logger.info("Generated scenarios: %s", comp)

    logger.info("✅ Blueprint scaffolding complete for **%s**.", module_name)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        logger.error("Usage: python scaffold_docs.py [root] [module] [subs...]")
        sys.exit(1)
    else:
        try:
            create_nibandha_docs(sys.argv[1], sys.argv[2], sys.argv[3:])
        except Exception as e:
            logger.exception("Scaffolding Failure: %s", e)
            sys.exit(1)