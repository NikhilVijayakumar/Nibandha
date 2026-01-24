# Package Dependency Report - E2E Tests

## Purpose
Verify full generation of Package Dependency Report.

---

## Scenarios

### PD-E2E-001: Full Gen (Current Env)
**Description**: Run against current environment.
**Verify**: 
- Generates valid report.
- Successfully calls `pip` (mocked or real).
- Image generated.

### PD-E2E-002: Mocked Outdated
**Description**: Mock pip returning 5 outdated packages.
**Verify**: Report lists 5 packages in outdated table.

### PD-E2E-003: Mocked Tree Viz
**Description**: Verify graph geneartion from mock dependency tree.
**Verify**: PNG creation.
