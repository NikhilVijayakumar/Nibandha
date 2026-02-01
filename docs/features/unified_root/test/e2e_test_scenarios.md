# Unified Root E2E Test Scenarios

## Overview
E2E tests verify the full lifecycle of the application initialization process on a real filesystem.

## Scenarios

### Positive Cases
| ID | Scenario | Description |
| :--- | :--- | :--- |
| **ROOT-E2E-001** | **Full Bind Cycle** | Init `Nibandha`, call `bind()`, verify directory tree exists on disk, check `Nibandha.initialized` log. |
| **ROOT-E2E-002** | **Idempotency** | Call `bind()` twice on the same instance. Verify no errors and no duplicate/corrupted state. |

### Negative Cases
| ID | Scenario | Description |
| :--- | :--- | :--- |
| **ROOT-E2E-003** | **Invalid Config Path** | Provide a `config_dir` in `AppConfig` that points to a non-existent location (if expected to pre-exist) or a read-only location. |
| **ROOT-E2E-004** | **Corrupt Rotation Config** | Place a malformed `rotation_config.yaml` in the config dir. Verify fallback to defaults or graceful error. |

### Corner Cases
| ID | Scenario | Description |
| :--- | :--- | :--- |
| **ROOT-E2E-005** | **Pre-existing Garbage** | Create a file named `.Nibandha` (blocking the root dir) before running. Verify clear failure message. |
