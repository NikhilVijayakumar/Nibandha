# Reporting Module: Deep Coverage Analysis & Plan

## Goal
Achieve 100% robust test coverage for the Reporting module by systematically verifying each reporter against deep logic, corner cases, and validation scenarios.

## Current Status (Post-Phase 1)
- **Unit Reporter**: 100% Coverage (Happy Path, Zero Tests, Grade Logic).
- **Quality Reporter**: 100% Coverage (Integration, Parsers).
- **Dependency Reporter**: 100% Coverage (Scanner, Graph Logic).
- **Overall**: ~45% Coverage.

## Remaining Gaps
1.  **Documentation Reporter**: `documentation_reporter.py` (14KB) is completely untested. Complex logic includes:
    - Drift calculation (timestamp comparison).
    - File scanning (Functional/Technical/Test/E2E docs).
    - Grade calculation based on drift and presence.
2.  **E2E Reporter**: `e2e_reporter.py` (9KB) covers E2E specific metrics. Untested logic:
    - Parsing `pytest-json` for "tests" vs "scenarios".
    - Visualization calls.
3.  **Introduction Reporter**: `introduction_reporter.py`. Simple but needs verification.
4.  **Summary/Unified Logic**: `SummaryDataBuilder` in `data_builders.py`. Aggregates all reports.
    - Grade aggregation logic (Weighted average?).
    - Status rollup (FAIL in one -> CRITICAL overall).

## Phase-by-Phase Execution Plan

### Phase 1: E2E & Introduction (Quick Wins)
- **Target**: `e2e/application/e2e_reporter.py`, `introduction/application/introduction_reporter.py`.
- **Scenarios**:
    - [ ] `RPT-E2E-001`: Generate report with passing scenarios (Happy Path).
    - [ ] `RPT-E2E-002`: Handle partial failures and empty suites.
    - [ ] `RPT-INT-001`: Verify introduction page rendering.

### Phase 2: Documentation Reporter (Deep Logic)
- **Target**: `documentation/application/documentation_reporter.py`.
- **Scenarios**:
    - [ ] `RPT-DOC-001`: Scan Functional/Technical docs (Mocked Filesystem).
    - [ ] `RPT-DOC-002`: Verify Drift Logic (Code timestamp vs Doc timestamp).
    - [ ] `RPT-DOC-003`: Grade Calculation (Drift penalties).
    - [ ] `RPT-DOC-004`: Handle missing documentation gracefully.

### Phase 3: Shared Infrastructure & Summary
- **Target**: `shared/data/data_builders.py`, `shared/infrastructure/utils.py`.
- **Scenarios**:
    - [ ] `RPT-SUM-001`: Verify Summary Aggregation (Unified Grade).
    - [ ] `RPT-SUM-002`: Verify Overall Status Logic (Critical triggers).
    - [ ] `RPT-UTL-001`: Verify `get_all_modules` recursion and filtering.

### Phase 4: Final Polish & Documentation
- Update `system/full_generation_scenarios.md`.
- Final `verify_system` run.

## Strategy for "Deep Analysis"
For each reporter, we will explicitly test the **internal logic** (private methods if necessary for complex algorithms like Drift) to ensure robustness against future refactoring.
