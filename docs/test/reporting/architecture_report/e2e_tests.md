# Architecture Report - E2E Tests

## Purpose
Verify architecture report generation.

---

## Scenarios

### AR-E2E-001: Full Gen (Fail)
**Description**: Generate report with broken contracts.
**Verify**: Status FAIL, violations listed.

### AR-E2E-002: Full Gen (Pass)
**Description**: Generate report with full compliance.
**Verify**: Status PASS, all contracts green.

### AR-E2E-003: Not Configured
**Description**: Generate report without `.importlinter` config.
**Verify**: Status NOT CONFIGURED, helpful "how to config" text.
