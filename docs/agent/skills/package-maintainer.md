---
name: package-maintainer
description: Manages the library's public API (exports), dependency tree, and PyPI readiness.
---
# Package-Maintainer Workflow

## 1. The Public Interface (Internal vs. External)
- **Rule:** Just because a class is in `src/` doesn't mean the client should see it.
- **Exporting:** When a new Domain Model or Protocol is added, ask the user: "Should this be exposed in `src/nibandha/__init__.py` for the client?"
- **Encapsulation:** Keep Infrastructure implementations private unless the client needs to instantiate them directly.

## 2. Dependency Management (`pyproject.toml`)
- **Isolation:** Ensure `pydantic` and `pathlib` are in the main dependencies. 
- **Extras:** Ensure heavy tools like `pytest`, `mypy`, and `ruff` are strictly confined to the `[tool.poetry.group.dev]` or the `[project.optional-dependencies]` (reporting) section.
- **Consistency:** If a new dependency is added, verify it doesn't conflict with common versions used in AI agent frameworks (like CrewAI or LangChain).

## 3. Semantic Versioning
- **Check:** Before finalizing a change to a Pydantic Model in the `domain/`, check if it breaks existing logic in the "Usage" section of the `README.md`.
- **Suggestion:** Suggest a Patch (x.x.1), Minor (x.1.x), or Major (1.x.x) version bump based on the change type.