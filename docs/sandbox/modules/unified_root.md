
# Unified Root Sandbox Module (Strict Mode)

This module validates the `UnifiedRoot` directory creation logic under **strict configuration** conditions. As per the design philosophy, the `FileSystemBinder` does not perform data manipulation or defaulting; it expects a fully resolved `AppConfig` object (populated by the Loader/Validator before binding).

**Module Name:** `unified_root`  
**Location:** `tests/sandbox/unified_root`

## Verification Philosophy

Tests in this module use a **Full, Explicit JSON Configuration** template (matching the production schema) to ensure:
1.  **No Implicit Defaults:** The binder creates exactly what is specified in the config.
2.  **Full Context:** Every test case provides a complete application state (Logging, Reporting, Export, Unified Root) to screen for side-effects.

## Verified Scenarios

### 1. Happy Path (`happy_path/test_ur_happy.py`)

| Scenario | Input Configuration (Summary) | Expected Output (Directory Structure) |
| :--- | :--- | :--- |
| **Full Explicit Config** | Standard ".Nibandha" structure explicit in all fields (`log_dir`, `output_dir`, etc.) | **Exact Match:**<br>`.Nibandha/logs`<br>`.Nibandha/Report`<br>`.Nibandha/config` |
| **Custom App Explicit** | Changed `name="MyApp"`, configures custom paths (`.MyRoot/custom_logs`). | **Exact Match:**<br>Creates `.MyRoot` and nested custom folders as defined. |
| **Multi-App Integrity** | Two apps sharing `.SharedRoot`. | **Isolation Verified:**<br>`.SharedRoot/AppA/config`<br>`.SharedRoot/AppB/config`<br>No shared config at root level. |

### 2. Corner Cases (`corner_cases/test_ur_corner.py`)

| Scenario | Details | Expectation |
| :--- | :--- | :--- |
| **Idempotency (Strict)** | Run binder with strict config on *pre-existing* directories containing data. | **Success**: Existing files are preserved (not wiped). |
| **Project Fallback (Strict)** | Config omits `name` and `unified_root.name`. Sandbox mocks `pyproject.toml`. | **Integration Success**: `AppConfig` resolves defaults from toml *before* binding.<br>Binder successfully creates `.MockedProject`. |

### 3. Failures (`failures/test_ur_failures.py`)

| Scenario | Input | Expectation |
| :--- | :--- | :--- |
| **Invalid Path Characters** | Strict config with invalid chars in `name`. | **OSError**: System refuses to create invalid paths. |

## Key Behavior: Config Isolation
The `config` directory is automatically namespaced to the Application Base directory (`Root/App/config` or `Root/config` in single-app mode). This ensures that multiple applications sharing a Unified Root do not overwrite each other's runtime configurations.
