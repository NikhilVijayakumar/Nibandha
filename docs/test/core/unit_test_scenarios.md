# Core Module Unit Test Scenarios

## Overview
The Core module handles application initialization, configuration loading (`AppConfig`), and directory structure management.

## Scope
- `AppConfig` validation and defaults.
- Root directory and standard folder creation.
- Custom folder creation.
- Rotation-specific folder structure (Data/Archive) vs Legacy.

## Scenarios

| ID | Scenario | Description | Type |
| :--- | :--- | :--- | :--- |
| **CORE-001** | **AppConfig Defaults** | Verify default values for `AppConfig` (e.g., `log_level="INFO"`, no custom folders). | Positive |
| **CORE-002** | **Folder Structure** | Verify `Nibandha.bind()` creates the root, log, and any customized folders. | Positive |
| **CORE-003** | **Rotation Integration** | Verify `logs/data` and `logs/archive` are created when rotation is enabled, overriding simple `logs/`. | Positive |
