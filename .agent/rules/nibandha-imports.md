# Nibandha Absolute Import Rule

## 1. No Relative Imports
- **Prohibited:** Never use relative imports (e.g., `from . import`, `from ..utils import`).
- **Required:** Always use absolute imports starting from the top-level package name.
- **Package Name:** The package name is `nikhil.nibandha` (or as defined in `pyproject.toml`).

## 2. Import Resolution Workflow
Before writing any import statement:
1. **Identify Source Root:** Check `pyproject.toml` to confirm the package name and source directory.
2. **Absolute Pathing:** Structure every import from the root (e.g., `from nikhil.nibandha.domain.models.log_entry import LogEntry`).

## 3. Library Compatibility
- Ensure imports remain valid when the library is installed as a site-package via `pip` or `git`.
- This rule applies to both `src/` code and `tests/` (when importing from the library).