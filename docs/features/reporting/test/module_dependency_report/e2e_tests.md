# Module Dependency Report - E2E Tests

## Purpose
Verify full generation of Module Dependency Report.

---

## Scenarios

### MD-E2E-001: Full Gen (Healthy)
**Description**: Generate from clean project structure.
**Verify**: Status HEALTHY, graph image generated.

### MD-E2E-002: Full Gen (Cycles)
**Description**: Generate with forced circular dependency.
**Verify**: Status FAIL, cycle listed in text.

### MD-E2E-003: Graph Visualization
**Description**: Verify PNG image creation.
**Verify**: `assets/images/module_dependencies.png` exists and is valid image.

### MD-E2E-004: Empty Project
**Description**: Run on project with no source files.
**Verify**: Handles gracefully (0 modules), no crash.
