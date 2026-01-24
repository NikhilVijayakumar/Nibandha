import os
import sys
import logging
from pathlib import Path

# Configure library-grade logger
logger = logging.getLogger("scaffolder")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


def inject_template(path: Path, title: str, category: str):
    """Injects platform-agnostic boilerplate into new files."""
    if path.exists():
        # Skip if file exists
        return

    if category == "functional":
        content = f"""# {title}

## Overview
Describe what this module does in plain English.

## Capabilities
- **Feature A:** Description
- **Feature B:** Description

## Usage
How to use this component.
"""
    elif category == "technical":
        content = f"""# {title}

## Design Decisions
Why we chose this approach.

## Data Flow
Diagram or description of data movement.
"""
    elif category == "test":
        content = f"""# {title}

| ID | Scenario | Category | Expected |
|:---|:---|:---|:---|
| PREFIX-UT-001 | Happy Path | Unit | Success |
| PREFIX-UT-002 | Corner Case | Unit | Handled gracefully |
"""
    else:
        content = f"# {title}\n"

    path.write_text(content)


def create_project_docs(root_path: str, module_name: str, sub_modules: list):
    root = Path(root_path)
    mod_lower = module_name.lower()
    logger.info("🏗️ Building 'Trinity' Documentation for: **%s**", module_name)

    # Base path: docs/modules/{module}/
    base_doc_path = root / "docs" / "modules" / mod_lower
    
    # 1. Functional Docs
    func_dir = base_doc_path / "functional"
    func_dir.mkdir(parents=True, exist_ok=True)
    inject_template(func_dir / "README.md", f"{module_name} Functional Specs", "functional")
    logger.info("✅ Created Functional Docs")

    # 2. Technical Docs
    tech_dir = base_doc_path / "technical"
    tech_dir.mkdir(parents=True, exist_ok=True)
    inject_template(tech_dir / "architecture.md", f"{module_name} Architecture", "technical")
    logger.info("✅ Created Technical Docs")

    # 3. Test Docs
    test_dir = base_doc_path / "test"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Create Unit and E2E scenario blueprints
    inject_template(test_dir / "unit_test_scenarios.md", f"{module_name} Unit Scenarios", "test")
    inject_template(test_dir / "e2e_test_scenarios.md", f"{module_name} E2E Scenarios", "test")
    logger.info("✅ Created Test Docs")

    logger.info("🎉 Documentation scaffolding complete for **%s**.", module_name)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        logger.error("Usage: python scaffold_docs.py [root] [module] [subs...]")
        sys.exit(1)
    else:
        try:
            create_project_docs(sys.argv[1], sys.argv[2], sys.argv[3:])
        except Exception as e:
            logger.exception("Scaffolding Failure: %s", e)
            sys.exit(1)