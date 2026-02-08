# Configuration Sandbox Module

## Overview
The **Configuration Sandbox** validates the `AppConfig` system against a comprehensive set of real-world scenarios. It ensures that the configuration loader is robust, resilient to errors, and consistent across different formats.

**Total Scenarios Verified**: 33

## Feature Spotlight: Partial Fallback (Robustness)
The configuration system employs a **Robust Config Validator** that sanitizes input before loading. Unlike standard parsers that fail on the first error, this system:
1.  **Iterates Field-by-Field**: Validates each setting individually.
2.  **Isolates Failures**: If a specific field (e.g., `logging.enabled`) has an invalid type, *only that field* is discarded.
3.  **Retains Validity**: The rest of the valid configuration (e.g., `name`, `mode`) is preserved.
4.  **Graceful Defaults**: Invalid fields are seamlessly replaced by their default values.

---

## Metric: File Loading & Resilience
Tests the fundamental ability to load files and handle filesystem/format errors gracefully.

| Test Name | Input Description | Expected Output |
| :--- | :--- | :--- |
| **Load Valid YAML** | Valid `config.yaml` with `named="YamlTestApp"` and logging settings. | `AppConfig` object populated with YAML values. |
| **Load Valid JSON** | Valid `config.json` with `name="JsonTestApp"`. | `AppConfig` object populated with JSON values. |
| **Load Invalid Format (Fallback)** | File with unsupported extension (`config.txt`). | **Default** `AppConfig` (Fallback), valid object returned. |
| **Load Missing File (Fallback)** | Non-existent file path (`non_existent.yaml`). | **Default** `AppConfig` (Fallback), valid object returned. |
| **Load Validation Error (Robust)** | `logging` field as a `string` instead of `object`. | `AppConfig` with default `LoggingConfig`. Invalid field ignored/reset. |
| **Sync Quality Target** | Minimal config. `pyproject.toml` present with `package-dir` mapping. | `reporting.quality_target` synced from `pyproject.toml` (e.g. `src/nikhil`). |
| **Sync Package Roots** | Minimal config. `pyproject.toml` present. | `reporting.package_roots` synced from `project.name`. |
| **Config Portability** | Empty config. | All path fields (templates, styles) are **explicit relative paths** (no absolute paths). |

---

## Metric: JSON Happy Path
Verifies correct parsing and logic for valid JSON configurations.

| Test Name | Input Description | Expected Output |
| :--- | :--- | :--- |
| **JSON - Empty Object** | `{}` | `AppConfig` with all default values (`name="Nibandha"`, `mode="production"`). |
| **JSON - Single Module (Logging)** | `{"logging": {"enabled": true, "level": "DEBUG"}}` | `AppConfig` with custom logging; other modules default. |
| **JSON - Full Configuration** | Full JSON object with all sections (`logging`, `reporting`, `export`, etc.). | `AppConfig` with all fields strictly matching input values. |
| **JSON - Unified Root Sync** | `{"name": "SyncApp"}` (No unified root specified). | `unified_root.name` auto-set to `.SyncApp` (matches App Name). |
| **JSON - Path Resolution (Single App)** | `{"name": "MyApp"}` | **Single App Mode**: Logs at `.MyApp/logs`, Report at `.MyApp/Report`. |
| **JSON - Path Resolution (Multi App)** | `{"name": "OtherApp", "unified_root": {"name": ".System"}}` | **Multi App Mode**: Logs at `.System/OtherApp/logs`, Report at `.System/OtherApp/Report`. |
| **JSON - Module List Support** | `{"reporting": {"module_discovery": ["Auth", "Core"]}}` | `module_discovery` correctly loaded as `List[str]`. |
| **JSON - Extra Fields Ignored** | JSON with unknown fields (`"trash": "value"`). | `AppConfig` loaded successfully; unknown fields ignored. |

---

## Metric: Failures & Robustness
Verifies that the system degrades gracefully instead of crashing on bad inputs.

| Test Name | Input Description | Expected Output |
| :--- | :--- | :--- |
| **JSON - Malformed Syntax** | Missing comma in JSON (`{...`). | **Default** `AppConfig` (Fallback). JSON error caught and logged. |
| **JSON - Wrong Root Type** | JSON Array (`[...]`) config. | **Default** `AppConfig` (Fallback). Input ignored. |
| **JSON - Field Type Mismatch** | `{"logging": "enabled"}` (String instead of Dict). | `AppConfig` with default `LoggingConfig`. Valid fields (`name`) retained. |

---

## Metric: Corner Cases & Coercion
Verifies Pydantic v2 data coercion and logic for edge cases.

| Test Name | Input Description | Expected Output |
| :--- | :--- | :--- |
| **JSON - Type Coercion (Bool)** | `{"logging": {"enabled": "true"}}` | `enabled=True` (Coercion successful). |
| **JSON - Type Coercion (Int)** | `{"rotation_interval_hours": "24"}` | `rotation_interval_hours=24` (Coercion successful). |
| **JSON - Float to Int** | `{"rotation_interval_hours": 24.9}` | `rotation_interval_hours=24` (Truncated/Coerced). |
| **JSON - Empty Path String** | `{"reporting": {"output_dir": ""}}` | `output_dir=Path(".")` (Current Directory). |
| **Export Defaults - Inheritance** | `export.input_dir = null`, `reporting.output_dir = "custom"` | `export.input_dir` defaults to `custom/details`. |
| **Export Defaults - Override** | `export.input_dir = "explicit"`, `reporting.output_dir = "custom"` | `export.input_dir` is `explicit` (Override respected). |

---

## Metric: Environment Integration
Verifies interaction with the runtime environment (`pyproject.toml`, CWD).

| Test Name | Input Description | Expected Output |
| :--- | :--- | :--- |
| **Pyproject Inheritance** | `pyproject.toml` with `name="Custom"` and `package-dir="src/lib"`. | `AppConfig` inherits `name="Custom"` and `quality_target="src/lib"`. |
| **Pyproject Missing (Fallback)** | No `pyproject.toml` in CWD. | `AppConfig` uses hardcoded defaults (`name="Nibandha"`, `quality_target="src"`). |

---

## Metric: Format Parity
Verifies that YAML and Dictionary inputs behave identically to JSON.

| Test Name | Input Description | Expected Output |
| :--- | :--- | :--- |
| **YAML - Full Configuration** | Full YAML object. | Identical `AppConfig` to JSON Full Config. |
| **YAML - Malformed Syntax** | Invalid YAML indentation/syntax. | **Default** `AppConfig` (Fallback). Error logged. |
| **Dict - Full Configuration** | Python Dictionary input. | Identical `AppConfig` to JSON Full Config. |

---

## Metric: Mixed Validity & Partial Recovery
Verifies "True Robustness": Valid fields are preserved while only invalid fields fall back to defaults.

| Test Name | Input Description | Expected Output |
| :--- | :--- | :--- |
| **JSON - Mixed Validity** | `{"name": "MixedApp", "logging": "invalid"}` | `name="MixedApp"` (Retained), `logging`=Default (invalid type handled). |
| **YAML - Recursive Recovery** | Valid `project_name`, Invalid `doc_paths` (List vs Dict). | `project_name` retained. `doc_paths` defaults to standard map. |
| **Dict - Mixed Validity** | `{"mode": "dev", "logging": 12345}` | `mode="dev"` retained. `logging` defaults (int rejected). |
