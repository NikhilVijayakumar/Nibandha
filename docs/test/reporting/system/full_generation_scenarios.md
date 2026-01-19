# System Integration Scenarios

## Overview
These scenarios cover the **ReportGenerator** as a whole, verifying that all sub-components (reporters) work together in the full pipeline.

---

## Scenarios

### SYS-001: Generate All (Happy Path)
**Description**: Run `generate_all()` with valid inputs.
**Expected**:
- Root output directory created.
- Subdirectories `details`, `assets/images`, `assets/data` created.
- **7 Detailed Reports** generated in `details/`.
- **1 Summary Report** generated in root.
- **Images** created in `assets/images`.
- **JSON Data** created in `assets/data`.
- All inter-report links valid.

### SYS-002: Partial Generation
**Description**: Run specific reporters (e.g., `unit=True`, `e2e=False`).
**Expected**:
- Only requested reports generated.
- Summary report reflects N/A for skipped reports.

### SYS-003: Clean Output Directory
**Description**: Run generation on non-empty directory.
**Expected**:
- Old reports overwritten/cleaned.
- No stale files linked.

### SYS-004: Missing Tools Handling
**Description**: Tools (mypy, ruff) not installed/failing.
**Expected**:
- System does not crash.
- Affected reports show error status.
- Other reports generate normally.

### SYS-005: Custom Templates Global
**Description**: Provide global template directory override.
**Expected**:
- All reporters attempt to use templates from custom dir.
- Fallback to default if specific template missing.

### SYS-006: Documentation Sync
**Description**: Verify `docs_dir` (test inventory) integration.
**Expected**:
- Test Inventory data included in report data (if feature enabled).
