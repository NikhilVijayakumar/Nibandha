# CR-001: Code Hygiene Reporting Module

## 1. Summary
Implement a **"Code Hygiene"** reporter in `Nibandha` to automatically detect maintenance anti-patterns that are not covered by standard linters or complexity checks.

## 2. Problem Statement
Developers often introduce "Magic Numbers", "Hardcoded Paths", and "Forbidden Functions" (e.g., `print`, `sys.path`) during rapid development. These issues reduce maintainability and break portability, yet pass standard "Style" checks.

## 3. Proposed Solution
Create `nibandha.reporting.quality.hygiene` using Python's `ast` module.

### Core Checks
1.  **Magic Numbers**: Detect numeric literals (excluding 0, 1, -1) not assigned to constants.
2.  **Hardcoded Paths**: Detect strings containing `/` or `\` that look like file paths.
3.  **Forbidden Functions**: Flag usage of:
    -   `print()` (should use `logging`)
    -   `sys.path.append/insert` (should use configuration)
    -   `pdb.set_trace` (debug leftovers)

### Implementation Details
-   **Visitor Pattern**: Extend `ast.NodeVisitor`.
-   **Configuration**: Add `hygiene` section to `nibandha.yaml` for ignore lists.
-   **Output**: New section "Code Hygiene" in `02_quality_report.md`.

## 4. Value Proposition
-   **Maintainability**: Enforces usage of constants and config.
-   **Portability**: Prevents hardcoded paths that break on other machines.
