# Type Safety Rules

## 1. Zero "Any" Policy
-   **Strict Ban:** Do not use `Any` unless absolutely unavoidable (e.g., interacting with a typeless 3rd party library).
-   **Mitigation:** If you must use `Any`, you MUST comment with `# type: ignore[misc]` and explain why.

## 2. Pydantic Over Dicts
-   **Data Structures:** Do not pass raw dictionaries (`Dict[str, Any]`) between layers.
-   **Model Usage:** Always define a Pydantic model (`frozen=True`) for structured data.

## 3. Protocols for Interfaces
-   **Decoupling:** Do not type-hint concrete classes (e.g., `def fn(repo: SqlManager)`).
-   **Abstraction:** Use Protocol definitions (e.g., `def fn(repo: StorageProtocol)`).

## 4. Return Types
-   **Mandatory:** Every function/method signature MUST include a return type annotation (`-> None`, `-> int`, etc.).
