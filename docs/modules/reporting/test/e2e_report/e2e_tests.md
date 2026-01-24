# E2E Test Report - E2E Tests

## Purpose
Verify full generation of E2E Report.

---

## Scenarios

### E2E-E2E-001: Full Gen
**Description**: Generate from valid E2E result JSON.
**Verify**: Markdown and 2 images (status + durations) generated.

### E2E-E2E-002: Missing Duration Data
**Description**: Handle case where duration is missing/zero.
**Verify**: Duration chart skipped or handles gracefully.

### E2E-E2E-003: No E2E tests found
**Description**: No tests match E2E filter.
**Verify**: Report indicates "No tests run", Status N/A.
