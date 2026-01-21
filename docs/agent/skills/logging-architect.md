---
name: logging-architect
description: GUIDELINE. Ensures implementation includes structured, traceable logging using Protocols.
priority: standard
---
# Logging-Architect Standards

When the Clean-Implementation agent builds a module, it must follow these logging patterns to ensure **"Library-Grade Traceability."**

## 1. Traceability Architecture
Every log entry must be structured to allow a developer to trace a request from entry to exit.
- **Contextual Logging:** Every class should initialize a local logger: `logger = logging.getLogger(__package__ + "." + __class__.__name__)`.
- **Event IDs:** Critical logic paths (like file deletion or network calls) must log their specific **Test ID** (e.g., `[AR-E2E-005] Starting atomic write...`).

## 2. Protocol & Interface
- **Dependency Inversion:** The core logic must depend on a `LoggerProtocol`, not the standard Python `logging` library directly. This allows for "Silent Testing" by injecting a Mock Logger during Stage 2.
- **Minimal Interface:** Protocol must support `debug`, `info`, `warning`, `error`, and `critical`.

## 3. Configuration Contract
- **Pydantic Validation:** All logging configurations must be handled via a `LogSettings` model.
- **Immutable Settings:** Use `model_config = ConfigDict(frozen=True)` to prevent runtime tampering with log levels.

## 4. The "Zero-Print" Guardrail
- **Detection:** Scan implementation for `print()`. If found, replace with `logger.debug()` or `logger.info()`.
- **Initialization:** Ensure that no log files are created on disk during the *import* of a module. File creation must only happen during the explicit `setup()` phase.