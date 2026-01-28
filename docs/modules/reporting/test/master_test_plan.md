# Reporting Module Master Test Plan

> [!IMPORTANT]
> This document defines the strategy for achieving 100% robust test coverage for the Reporting module. All changes to the module must verify against these scenarios.

## 1. Unit Reporter Scenarios
| ID | Title | Description | Priority | Included? |
|---|---|---|---|---|
| RPT-UT-001 | Happy Path Generation | Verify report generation with valid pytest and coverage data. | High | ✅ |
| RPT-UT-002 | Missing Coverage Data | Verify behavior when coverage data is None or empty options. | Medium | ✅ |
| RPT-UT-003 | Zero Tests | Verify behavior when test suite is empty (no crash, empty tables). | Medium | ❌ |
| RPT-UT-004 | Module Grouping | Verify tests are grouped correctly into modules (e.g. Rotation->Logging). | Low | ✅ |
| RPT-UT-005 | Grade Calculation | Verify correct grade logic (pass rate + coverage rate). | High | ❌ |

## 2. Quality Reporter Scenarios
| ID | Title | Description | Priority | Included? |
|---|---|---|---|---|
| RPT-QI-001 | Check Integration | Verify `run_checks` calls subprocess for architecture/type/complexity. | High | ✅ |
| RPT-QI-002 | Happy Path Generation | Verify report generation from clean check results. | High | ✅ |
| RPT-QI-003 | Parser: MyPy | Verify `_parse_mypy_output` correctly extracts module counts and categories from raw text. | Medium | ❌ |
| RPT-QI-004 | Parser: Ruff | Verify `_parse_ruff_output` correctly extracts C901 violations per file. | Medium | ❌ |
| RPT-QI-005 | Missing Config | Verify graceful handling when `.importlinter` or config files are missing. | Low | ❌ |

## 3. Dependency Reporter Scenarios
| ID | Title | Description | Priority | Included? |
|---|---|---|---|---|
| RPT-DP-001 | Scan Package | Verify `PackageScanner` parses `pyproject.toml` correctly. | High | ❌ |
| RPT-DP-002 | Graph Generation | Verify `DependencyReporter` builds graph nodes from module imports. | High | ❌ |
| RPT-DP-003 | Circular Deps | Verify detection of circular dependencies. | Medium | ❌ |

## 4. Shared Infrastructure Scenarios
| ID | Title | Description | Priority | Included? |
|---|---|---|---|---|
| RPT-SH-001 | Data Builder Logic | Verify `UnitDataBuilder` grade and status calculation rules isolated from IO. | High | ❌ |
| RPT-SH-002 | Utils | Verify helper functions (`extract_module_name`) handle edge cases. | Low | ❌ |

## 5. Summary Reporter Scenarios
| ID | Title | Description | Priority | Included? |
|---|---|---|---|---|
| RPT-SM-001 | Aggregation | Verify summary report correctly aggregates status integers from all sub-reports. | High | ❌ |
