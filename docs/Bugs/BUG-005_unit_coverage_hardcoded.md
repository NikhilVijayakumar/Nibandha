# BUG-005: Hardcoded Unit Coverage Target

## 🔴 Status: Open
**Date:** 2026-02-04
**Component:** `Nibandha.Reporting.Unit`
**Severity:** Critical (Causes "F" Grade in correct projects)

## 🐛 Description
The `ReportGenerator` hardcodes the coverage target directory to `src/nikhil/nibandha` when running unit tests. This ignores the actual project source code (e.g., `src/bavans/tantra`), resulting in 0% reported coverage even if tests pass and coverage data is available for other paths.

## 📍 Location
- **File:** `nibandha/reporting/shared/application/generator.py`
- **Method:** `run_unit_Tests`
- **Line:** ~344

```python
cov_target = "src/nikhil/nibandha"
```

## 📉 Impact
- Any project not named "Nibandha" gets **0.0% Coverage**.
- Unit Test Grade is always **F**.
- Metrics are misleading.

## 🛠️ Reproduction
1. Run `verify_system.py` on a project with source in `src/foo/bar`.
2. Observe `03_unit_report.md`.
3. Coverage is 0.0% because `pytest-cov` only tracked `src/nikhil/nibandha`.

## ✅ Expected Behavior
The coverage target should be:
1. Passed as an argument to `run_unit_Tests`.
2. OR, derived from `ReportingConfig.quality_target`.
3. OR, default to `src/`.

## 🩹 Proposed Fix
Update `generator.py` to respect `self.quality_target_default` if `cov_target` is not explicitly provided.
