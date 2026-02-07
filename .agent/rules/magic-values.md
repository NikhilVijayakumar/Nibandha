# Magic Value & Hardcoding Rules

## 1. The "No Magic" Principle
Use named constants or configuration for ALL values. **Hardcoding strings or numbers in logic is strictly FORBIDDEN.**

## 2. Hardcoded Strings
-   **Forbidden:** `if role == "admin":`, `path = "/tmp/data"`
-   **Allowed:** 
    -   `if role == Roles.ADMIN:` (Enum)
    -   `path = PathConfig.TEMP_DATA` (Config class)
    -   `logger.info("Fixed message")` (Logging/Exception messages are exempt IF they are fixed templates).

## 3. Magic Numbers
-   **Forbidden:** `if retries < 3:`, `time.sleep(60)`
-   **Allowed:**
    -   `if retries < MAX_RETRIES:`
    -   `time.sleep(WAIT_INTERVAL_SECONDS)`

## 4. Where to Store Constants?
1.  **Domain Business Logic:** Usage specific Enums or `consts.py` in the Domain layer.
2.  **Configuration:** `config.py` using Pydantic `BaseSettings` for environment-dependent values.
3.  **Infrastructure:** `defaults.py` for fallback values.
