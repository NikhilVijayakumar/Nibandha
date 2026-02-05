# CR-003: Code Duplication Detection (DRY)

## 1. Summary
Implement a **Duplication Detector** to identify code clones and enforce the "Don't Repeat Yourself" (DRY) principle.

## 2. Problem Statement
Copy-pasted code spreads bugs and increases technical debt. If a bug is fixed in one copy but not the others, the system remains vulnerable. Standard coverage or complexity metrics do not detect this.

## 3. Proposed Solution
Implement a clone detection mechanism using AST subtree hashing or integrate tools like `pylint --enable=duplicate-code`.

### Core Checks
1.  **Block Duplication**: Identical code blocks > 10 lines.
2.  **Structural Duplication**: Code that is structurally identical (ignoring variable names) - *Advanced*.

### Implementation Details
-   **Module**: `nibandha.reporting.quality.duplication`.
-   **Algorithm**: Rabin-Karp or AST Hashing for efficiency.
-   **Output**: "Duplication Hotspots" table in `02_quality_report.md`.
-   **Config**: `min_similarity_lines` (default: 10).

## 4. Value Proposition
-   **Tech Debt Reduction**: Identifies opportunities for refactoring into shared functions.
-   **Bug Prevention**: Ensures fixes are applied centrally.
