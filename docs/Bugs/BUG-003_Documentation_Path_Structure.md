# BUG-003: Documentation Reporter Path Incompatibility

## 🔴 Issue Description
The `Nibandha` Documentation Reporter strictly hardcodes the search path for module documentation to `docs/modules/{module}/...`.
However, the `Tantra` project structure uses `docs/features/{module}/...`.

As a result, the Documentation Reporter fails to find existing markdown documentation, resulting in:
-   **Coverage**: 0%
-   **Grade**: F
-   **Status**: FAIL (Missing)

## 🔍 Root Cause
In `documentation_reporter.py`, the path resolution logic is rigid and does not support configuration or the `features` directory convention:
```python
# Current Logic (Hardcoded)
mod_func_dir = root / "docs" / "modules" / mod.lower() / "functional"
```

## 📉 Impact
-   The "Documentation Coverage" metric is technically false (reporting 0% when files exist).
-   The overall Project Grade is dragged down to **F** despite the existence of documentation.

## 🛠 Suggested Fix
Modify `documentation_reporter.py` to:
1.  Check for `docs/features` if `docs/modules` does not exist.
2.  Or make the documentation root configurable via `ReportingConfig`.

## 🔄 Current Workaround
None. Local patching of the library is **disallowed**. The report will remain failing until upstream `Nibandha` is patched.
