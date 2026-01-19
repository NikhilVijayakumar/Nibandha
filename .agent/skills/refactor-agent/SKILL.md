---
name: refactor-agent
description: Uses Nibandha quality reports to identify and fix architectural drift, complexity spikes, and dependency cycles.
---
# Refactor-Agent Workflow

Use this skill when a Quality Report indicates a 🔴 FAIL or ⚠️ WARN status.

## 1. Input Analysis
- **Complexity Fix:** If `complexity_report.md` shows a score > 10 (C901), break the offending function into smaller, private methods or move logic to a new `Service` class.
- **Dependency Fix:** If `module_dependency_report.md` shows a circular dependency, identify the shared logic and extract it into a new file in `domain/models/` or a shared `util`.
- **Type Safety:** If `type_safety_report.md` shows MyPy errors, update the Pydantic models or add proper Type Hints to the Protocols.

## 2. Refactoring Rules
- **Maintain SOLID:** Every refactor must move the code closer to Single Responsibility.
- **One File, One Class:** If a class grew too large, split it into multiple files.
- **No Regression:** After refactoring, immediately trigger the **Test-Scaffolder** or run the unit tests to ensure behavior hasn't changed.

## 3. Implementation
1. Read the specific report file in `.Nibandha/Report/`.
2. Locate the source code mentioned.
3. Propose the "Clean Architecture" solution (e.g., "Extracting logic to a UseCase").
4. Execute the change only after user confirmation.