# Git Cleanliness & Sandbox Rules

## 1. The Sandbox Rule
To prevent "Git Trash" (accidental commits of debug scripts, logs, temp data), we enforce a strict **Sandbox Policy**.

-   **All Temporary Files MUST be written to:** `.{ProjectName}/tmp/`
    -   *Example:* `Nibandha/.Nibandha/tmp/test_run_1.log`
-   **Derivation:** The `{ProjectName}` is derived dynamically from `pyproject.toml` (project.name).

## 2. Root Sanctity
The Project Root is **Sacred and Read-Only** for automated agents.

-   **Allowed Root Files:** `pyproject.toml`, `README.md`, `.gitignore`, `check_foundations.py` (if standard), config files.
-   **Forbidden:** `debug_*.py`, `temp_*.txt`, `verify_result.json`.
-   **Scripts:** All executable utilities must reside in `scripts/` or `.agent/skills/*/scripts/`.

## 3. Automation
-   **Analysis:** Agents must read `pyproject.toml` to find the correct temp path. Do not hardcode `.Nibandha`.
-   **Cleanup:** The `Mayavi` agent provides a cleanup routine to wipe the Sandbox directory.
