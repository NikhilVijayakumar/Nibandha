# Summary Report - Unit Tests

## Purpose
Verify aggregation logic.

---

## Scenarios

### SR-UT-001: Aggregation (Partial)
**Description**: Aggregate when only some reports ran.
**Expected**: Missing reports marked N/A, overall status calculated correctly.

### SR-UT-002: Overall Status (Fail)
**Description**: One sub-report fails.
**Expected**: Overall status FAIL (priority logic).

### SR-UT-003: Overall Status (Pass)
**Description**: All sub-reports pass.
**Expected**: Overall status PASS.

### SR-UT-004: Clean Metadata
**Description**: Ensure date/time generation is correct.
