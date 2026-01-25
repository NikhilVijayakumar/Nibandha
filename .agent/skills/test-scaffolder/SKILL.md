---
name: test-scaffolder
description: Dynamic TDD Scaffolder. Generates Unit and E2E test suites for N sub-modules plus Integration logic.
priority: critical
---
# Test-Scaffolder Workflow (Dynamic N+1 Pattern)

## 0. Activation & Triggers
*   **Trigger:** `"Scaffold Tests for [Module]"`
*   **Pre-requisites:** `docs/modules/[Module]/functional/README.md` must exist.
*   **Goal:** Create **failing** Pytest stubs (`RED` phase) that map 1:1 to the documented IDs.

Once the **Doc-Architect** has defined the components...

## 1. Discovery & Count ($N$)
- **Analyze Documentation:** Identify how many sub-modules ($N$) were defined in `docs/modules/`.
- **Identify Integration:** Identify the primary entry point (the "Glue") that coordinates the sub-modules.

## 2. Dynamic Scaffolding Rules
For every identified sub-module `{sub}`, and the final integration layer, create the following:

### A. Sub-Module Level ($N$ iterations)
- `tests/unit/{module}/{sub}/test_unit.py`: Isolated logic tests with mocks.
- `tests/e2e/{module}/{sub}/test_e2e.py`: Real filesystem/output tests using `tmp_path`.

### B. Integration Level (The +1 Layer)
- `tests/unit/{module}/integration/test_glue_unit.py`: Tests the wiring/contracts between sub-modules.
- `tests/e2e/{module}/integration/test_full_flow_e2e.py`: End-to-end lifecycle from trigger to final output.

## 3. Physical Requirements
- **Traceability:** Every test function must be decorated or commented with the Blueprint ID (e.g., `# ID: AR-UT-001`).
- **Fail-by-Default:** Tests should contain `pytest.fail("Implementation Pending")` or a failing `assert` until the Clean-Implementation agent builds the logic.
- **Cross-Platform:** Use `pathlib.Path` exclusively. No raw string paths.

## 4. Execution Logic
1. Create directory tree: `tests/{module}/{sub_1...sub_N}` and `tests/{module}/integration`.
2. Generate stubs for all identified scenarios.
3. **Sign-off:** "Scaffolded [2*N + 2] test files for {module}. The RED phase is active."