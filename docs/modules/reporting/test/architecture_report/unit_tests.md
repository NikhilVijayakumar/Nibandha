# Architecture Report - Unit Tests

## Purpose
Verify parsing of `import-linter` output.

---

## Scenarios

### AR-UT-001: Parse Broken Contract
**Description**: Extract contract name and violation details.
**Expected**: Contract marked as broken, violations list populated.

### AR-UT-002: Parse Kept Contract
**Description**: Identify successful contracts.
**Expected**: Contract marked as kept.

### AR-UT-003: Missing Configuration
**Description**: Detect when linter reports no config found.
**Expected**: Status set to NOT CONFIGURED.
