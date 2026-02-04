# BUG-004: Unit Documentation Lookup Failure

## 🔴 Status: Open
**Date:** 2026-02-04
**Component:** `Nibandha.Reporting.Unit`
**Severity:** Critical (Causes Documentation "F" Grade)

## 🐛 Description
The `UnitReporter` fails to detect documentation files located in the `test/` subdirectory, which is the structure expected by the `Nibandha` 1.0.6 unified documentation standard. It blindly looks for files in the parent module directory.

## 📍 Location
- **File:** `nibandha/reporting/shared/infrastructure/utils.py`
- **Function:** `get_module_doc`
- **Line:** 40

```python
doc_path = docs_dir / mod_lower / f"{report_type}_test_scenarios.md"
```

## 📉 Impact
- `unit_test_scenarios.md` files located in `docs/features/{mod}/test/` are ignored.
- Unit Report shows "No documentation found".
- Documentation Grade drops to "F".

## 🛠️ Reproduction
1. Place `unit_test_scenarios.md` in `docs/features/semantic/test/`.
2. Run `verify_system.py`.
3. Check `03_unit_report.md`.

## ✅ Expected Behavior
The utility should check:
1. `docs/features/{mod}/{type}_test_scenarios.md` (Legacy)
2. `docs/features/{mod}/test/{type}_test_scenarios.md` (Unified)

## 🩹 Proposed Fix
Patch `utils.py` to add array-based path checking.
