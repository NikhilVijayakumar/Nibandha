# START: DRY (Don't Repeat Yourself) Rules

## 1. The Rule of Three
-   **Refactor Trigger:** If you copy-paste logic **three times**, you MUST extract it into a shared function, class, or constant.

## 2. Common Patterns
-   **Constants:** Magic strings/numbers repeated > 2 times must be moved to `constants.py` or an Enum.
-   **Logic:** Repeated `try/except` blocks or validation logic must be moved to a decorator or a utility function.
-   **Tests:** Repeated setup code in tests must be moved to a `pytest.fixture`.

## 3. Scope of Sharing
-   **Module Level:** Share within the module first (private `_helper`).
-   **Package Level:** Share within the package (`shared/utils.py`).
-   **Global:** Only if truly generic (e.g., Date/Time utils). Do not create a "God Object" `utils.py`.
