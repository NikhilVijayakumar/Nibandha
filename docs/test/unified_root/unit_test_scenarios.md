# Unified Root Unit Test Scenarios

## Overview
The Unified Root module (`nibandha.unified_root`) handles the workspace lifecycle: calculating paths (`RootContext`), creating directories (`FileSystemBinder`), and orchestration (`Nibandha` Facade).

## Scope
- `RootContext` Immutability and Path Calculation.
- `FileSystemBinder` directory creation logic.
- `Nibandha` Facade orchestration.

## Scenarios

### Positive Cases
| ID | Scenario | Description |
| :--- | :--- | :--- |
| **ROOT-POS-001** | **Context Calculation** | Verify `RootContext` correctly resolves paths based on `AppConfig`. |
| **ROOT-POS-002** | **Binder Creation** | Verify `FileSystemBinder.bind()` creates all expected directories (Root, App, Config, Reports, Logs). |
| **ROOT-POS-003** | **Custom Folder Creation** | Verify application-specific `custom_folders` are created. |
| **ROOT-POS-004** | **Rotation Integration** | Verify `logging/data` and `logging/archive` are created if Rotation Config is passed to Binder. |

### Negative Cases (Mocked FS)
| ID | Scenario | Description |
| :--- | :--- | :--- |
| **ROOT-NEG-001** | **Permission Denied** | Simulate `PermissionError` during `mkdir`. Verify binder raises appropriate exception or handles gracefully. |
| **ROOT-NEG-002** | **File Blocking Dir** | Simulate a file existing with the same name as a directory to be created. Verify failure. |

### Corner Cases
| ID | Scenario | Description |
| :--- | :--- | :--- |
| **ROOT-CNR-001** | **Immutability** | Verify `RootContext` attributes cannot be modified after creation. |
| **ROOT-CNR-002** | **Root at Drive Root** | Verify behavior when `root_name` is set to `/` or `C:/`. |
| **ROOT-CNR-003** | **Nested Custom Folders** | Verify `custom_folders=["a/b/c"]` creates the full deep structure. |
