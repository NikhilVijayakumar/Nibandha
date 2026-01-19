# Summary Report - E2E Tests

## Purpose
Verify generation of the Summary markdown file.

---

## Scenarios

### SR-E2E-001: Full Gen
**Description**: Generate summary after all other reports generated.
**Verify**: 
- `overview.md` (or `summary.md`) created.
- Links to detailed reports are valid.
- Embedded images exist.

### SR-E2E-002: Fresh Run
**Description**: Run summary builder with no existing data files.
**Verify**: Report generated with "N/A" for all sections, no crash.
