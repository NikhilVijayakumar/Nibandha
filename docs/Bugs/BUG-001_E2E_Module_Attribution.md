# BUG-001: E2E Module Attribution Failure

## Description
The End-to-End (E2E) Test Report (`04_e2e_report.md`) incorrectly groups all integration tests under the "Other" category, leaving core modules (Semantic, Entity, etc.) with 0 attributed tests.

## Root Cause
The `e2e_reporter.py` logic relies on specific directory structures (`e2e/{module}` or `domain/{module}`) to identify the module name from the test node ID.
The current project structure uses flattened integration tests: `tests/integration/test_{module}_integration.py`. The reporter fails to parse the module name from this filename pattern.

## Impact
-   Module-specific E2E coverage metrics are inaccurate (always 0).
-   "Other" category is bloated.
-   Overall project grade is affected if module-specific thresholds are enforced.

## Proposed Fix
Update `_resolve_test_module` in `e2e_reporter.py` to support regex-based extraction from filenames:
```python
# Support Pattern: test_{module}_integration.py
match = re.search(r"test_([a-z]+)_integration", filename)
if match:
    return match.group(1).capitalize()
```
