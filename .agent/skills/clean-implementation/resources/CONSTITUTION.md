This **`CONSTITUTION.md`** serves as the ultimate source of truth for the `clean-implementation` agent. It bridges the gap between high-level architectural philosophy and the physical reality of the code.

---

# 📜 NIBANDHA IMPLEMENTATION CONSTITUTION

## PREAMBLE

This document defines the non-negotiable standards for the Nibandha system. Every line of code must be a testament to **Stability, Traceability, and Portability.** We do not write scripts; we build a production-grade library ecosystem.

---

## PILLAR 1: ZERO-HIDDEN STATE

### Rule: Constructor-Based Dependency Injection (DI)

**Standard:** All implementation classes must be "born" with their dependencies. Using global configurations or instantiating services inside a class is strictly prohibited.

* **The Guardrail:** Logic interacts only with **Protocols** and **Pydantic Models** passed via `__init__`.
* **Failure Prevented:** "Ghost Bugs" caused by shared global state across test suites.
* **The Win:** 100% Mockability for TDD.

---

## PILLAR 2: IMMUTABLE PACKAGE IDENTITY

### Rule: Absolute Import Enforcement

**Standard:** Every import must be a full map coordinate. Relative imports (`from .`) are illegal.

* **Root:** All internal imports must start with the package root (e.g., `from nikhil.nibandha...`).
* **Failure Prevented:** "Import Hell" crashes when the library is installed as a pip package or used in different environments.
* **The Win:** Seamless portability across Cloud, Edge, and Desktop.

---

## PILLAR 3: THE IMMUTABLE CONTRACT

### Rule: Frozen Pydantic Domain Models

**Standard:** Data structures are shields, not just containers.

* **Config:** Models must use `ConfigDict(frozen=True, strict=True, extra='forbid')`.
* **Failure Prevented:** "State Poisoning" where one module accidentally alters a configuration value used by another.
* **The Win:** Kotlin-like predictability where data remains constant throughout the execution lifecycle.

---

## PILLAR 4: SEMANTIC LOGGING

### Rule: The Blueprint-to-Binary Bridge

**Standard:** Logs are structured audit trails.

* **Requirement:** Every primary logic gate must emit a log containing its **Blueprint ID** (e.g., `[AR-UT-007]`).
* **Failure Prevented:** "Log Noise"—spending hours guessing which architectural requirement failed.
* **The Win:** Deep Traceability. One log line connects the Code, the Test, and the Requirement.

---

## 🛠️ MANDATORY VALIDATION WORKFLOW

Before any task is marked **DONE**, the agent must execute and pass the following gatekeepers:

1. **`verify_structure.py`**: Ensures "One Class, One File" and no nested logic.
2. **`verify_imports.py`**: Validates that 100% of imports are Absolute.
3. **`validate_traceability.py`**: Confirms that every ID in the documentation exists in the implementation's logs.

---

### 💡 Final Implementation Checklist for the Agent

* [ ] Is the file named `snake_case.py` and the class `PascalCase`?
* [ ] Does the import start with `nikhil.nibandha`?
* [ ] Is the settings model `frozen=True`?
* [ ] Does the constructor inject a **Protocol** instead of a concrete class?
* [ ] Is there a log line for every Scenario ID?

**Would you like me to generate the "Project Root Configuration" (pyproject.toml) that defines `nikhil.nibandha` as the official package root to support these rules?**