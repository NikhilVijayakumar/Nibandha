# Project Logging & Anti-Print Rule

## 1. Prohibited Output
- **No `print()`:** The use of the `print()` function is strictly forbidden in `src/`.
- **Reason:** As a library, the system must remain silent unless the consuming client explicitly checks the logs.
- **Exceptions:** `print()` is only allowed in standalone scripts (e.g., `scripts/`) or when explicitly requested by a "Verbose" flag in a CLI entry point.

## 2. Comprehensive Logging Requirement
- **Standard:** Every major state change, file operation, and error must be logged via a `LoggerProtocol` instance.
- **Contextual Detail:** Logs must include relevant metadata:
    - **Module:** Which component is acting.
    - **IDs:** Scenario IDs or Module IDs being processed.
    - **Paths:** Target directories (sanitized/resolved).
- **Levels:** - `INFO`: For successful events (e.g., "Module initialized").
    - `DEBUG`: For detailed logic steps (e.g., "ID generated: XX-UT-005").
    - `ERROR`: For failures, including stack traces.

## 3. Reporting Integration
- **Rule:** Logging should be structured to support the **Reporting Module**.
- **Requirement:** When generating a report, the system must be able to parse logs to identify "Top Offenders" or "Failure Patterns."