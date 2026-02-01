# Configuration Module Unit Test Scenarios

## Overview
The Configuration module (`nibandha.configuration`) is responsible for defining and loading application settings (`AppConfig`).

## Scope
- **Domain:** `AppConfig` Pydantic model validation.
- **Infrastructure:** `StandardConfigLoader` behavior.

## Scenarios

### Positive Cases (Happy Path)
| ID | Scenario | Description |
| :--- | :--- | :--- |
| **CFG-POS-001** | **Default Initialization** | Initialize `AppConfig` with only `name`. Verify `log_level="INFO"` and `custom_folders=[]`. |
| **CFG-POS-002** | **Full Initialization** | Initialize with all optional fields (log_dir, etc.). Verify values are persisted. |
| **CFG-POS-003** | **Loader Pass-Through** | Verify `StandardConfigLoader.load()` correctly maps constructor args to `AppConfig`. |

### Negative Cases (Error Handling)
| ID | Scenario | Description |
| :--- | :--- | :--- |
| **CFG-NEG-001** | **Missing Required Field** | Attempt to create `AppConfig` without `name`. Verify `ValidationError`. |
| **CFG-NEG-002** | **Invalid Type** | Pass `custom_folders` as a string instead of a list. Verify `ValidationError`. |
| **CFG-NEG-003** | **Invalid Log Level??** | *Note: Currently validation is weak (str).* Check if validation fails for non-standard levels if using Enum (Future). |

### Corner Cases (Edge Boundaries)
| ID | Scenario | Description |
| :--- | :--- | :--- |
| **CFG-CNR-001** | **Empty Strings** | Pass empty string for `name`. *Should likely fail or be handled upstream.* |
| **CFG-CNR-002** | **Path Traversal** | Pass `../../etc/passwd` or similar as a custom folder. *Security check.* |
| **CFG-CNR-003** | **Unicode Names** | Pass Emoji or complex Unicode as `name`. Verify handled correctly in path generation. |
