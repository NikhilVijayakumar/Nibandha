# Project Testing & Quality Rule

## 1. Scenario-Based Structure 
- **Granularity:** One Scenario = One File. Do not group multiple scenarios in one file.
- **Organization:** - Unit Tests: `tests/unit/<module>/<component>/test_{id}_{slug}.py`
  - E2E Tests: `tests/e2e/<module>/<component>/test_{id}_{slug}.py`

## 2. Strict Naming Convention (Pytest Unique Basenames)
All test files MUST follow the pattern: `test_{id}_{slug}.py`
- `{id}`: Lowercase Scenario ID from docs (e.g., `PREFIX-UT-001` becomes `prefix_ut_001`).
- `{slug}`: A brief snake_case description.
- **Correct Example:** `test_ar_ut_001_extraction.py`
- **Correct Example:** `test_rotation_005_limit_reached.py`

## 3. Workflow: Documentation-First
Before creating or modifying a test:
1.  **Read/Update Documentation:** Check `docs/modules/<module>/test/unit_test_scenarios.md` (or `e2e`).
2.  **Verify ID:** Ensure the `{id}` in the filename matches the ID in the documentation table.
3.  **Implement:** The code must map 1:1 to the documented scenario.

## 4. "No Workarounds" Policy
- **No Monkey-Patching:** Only mock external systems (FS, Network, Time). Do not patch internal logic to bypass complexity.
- **Fix the Source:** If a test fails due to design flaws (like state leakage), modify the source code, not the test.
- **OS Agnostic:** Use `pathlib` for all paths. Ensure compatibility with Windows, Linux, and macOS.

## 5. Isolation & Cleanup
- **Filesystem:** Always use the `tmp_path` fixture. Never write to the real project root.
- **State:** Use fixtures to reset logs/handlers after every test run.