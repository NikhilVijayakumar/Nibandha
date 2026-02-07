# Agent Independence Rules

## 1. The Separation of Church and State
The `.agent` directory (The Brain) must remain completely independent of the `src/` directory (The Body).

-   **Forbidden:** `.agent` scripts/skills importing the **Project Source Code** (defined in `pyproject.toml`).
-   **Allowed:** `.agent` scripts *reading* source files as text/AST.

## 2. Why?
-   **No Hallucinations:** The agent shouldn't execute project code that might be broken.
-   **No Circular Deps:** The agent tools must run even if the project is crashing.
-   **Portability:** The agent skills should be portable to other projects (mostly).

## 3. Enforcement
-   The **Compliance Officer** runs `scripts/verify_agent_independence.py` which dynamically reads the forbidden package name from `pyproject.toml`.

