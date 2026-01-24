# E2E Test Report - Unit Tests

## Purpose
Verify E2E-specific data parsing.

---

## Scenarios

### E2E-UT-001: Filter E2E Tests
**Description**: Ensure only tests marked as E2E are included (exclude unit).
**Input**: Mixed json output.
**Expected**: Counts reflect only E2E tests.

### E2E-UT-002: Slowest Scenarios Sorting
**Description**: Correctly identify top N slowest tests.
**Expected**: Sorted descending by duration.

### E2E-UT-003: Failure Screenshot Linking
**Description**: If failure metadata contains screenshot path, include in output.
**Expected**: JSON includes `screenshot` field.
