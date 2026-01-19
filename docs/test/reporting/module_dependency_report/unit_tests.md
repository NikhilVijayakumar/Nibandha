# Module Dependency Report - Unit Tests

## Purpose
Verify dependency graph construction and cycle detection.

---

## Scenarios

### MD-UT-001: Build Graph from Imports
**Description**: Correctly identifies imports between mock files.
**Input**: File A imports B.
**Expected**: Graph edge A -> B exists.

### MD-UT-002: Detect Cycle (Direct)
**Description**: A imports B, B imports A.
**Expected**: Cycle detected.

### MD-UT-003: Detect Cycle (Indirect)
**Description**: A->B->C->A.
**Expected**: Cycle detected.

### MD-UT-004: Isolate stdlib
**Description**: Ignore imports like `os`, `sys`.
**Input**: File imports `os`.
**Expected**: No edge to `os` in internal graph.

### MD-UT-005: Identify Isolated Modules
**Description**: Module with no internal imports/exports.
**Expected**: Listed in `isolated_list`.

### MD-UT-006: Calculate Fan-in/Fan-out
**Description**: Verify "Most Imported" counts.
**Expected**: Correct numbering.
