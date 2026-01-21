# Logging Module Unit Test Scenarios

## Overview
The Logging module (`nibandha.logging`) provides structured, traceable logging.

## Scope
- `LogSettings` & `LogRotationConfig` validation.
- `NibandhaLogger` handler attachment and propagation.
- `RotationManager` archival logic.

## Scenarios

### Positive Cases
| ID | Scenario | Description |
| :--- | :--- | :--- |
| **LOG-POS-001** | **Standard Logging** | Verify info/debug logs appear in file with correct format and Trace IDs (if provided). |
| **LOG-POS-002** | **Handler Isolation** | Verify `nibandha` logs do not propagate to root logger (avoid double logging). |
| **LOG-POS-003** | **Rotation Trigger** | Verify `should_rotate()` returns True when file size exceeds limit (mocked). |
| **LOG-POS-004** | **Archival** | Verify `archive_old_logs()` moves files from data to archive dir. |

### Negative Cases
| ID | Scenario | Description |
| :--- | :--- | :--- |
| **LOG-NEG-001** | **Invalid Rotation Config** | Initialize `RotationManager` with missing/invalid config. Verify safe fallback. |
| **LOG-NEG-002** | **Directory Not Writable** | Simulate read-only `log_dir`. Verify logger handles `PermissionError` (e.g., emits to stderr or suppresses). |

### Corner Cases
| ID | Scenario | Description |
| :--- | :--- | :--- |
| **LOG-CNR-001** | **Massive IDs** | Pass a list of 1000+ IDs to `log.info(..., ids=[...])`. Verify performance/formatting resilience. |
| **LOG-CNR-002** | **Non-String Messages** | Log an object or `None` as message. Verify formatter handles `str(msg)` conversion safely. |
| **LOG-CNR-003** | **Rapid Rotation** | Simulate rapid log growth requiring multiple rotations in one second. Verify timestamp/sequence handling. |
