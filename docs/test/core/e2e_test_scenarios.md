# Core Module E2E Test Scenarios

## Overview
The Core E2E tests verify the full application lifecycle from initialization through logging, rotation, and cleanup.

## Scope
- Full application bind and initialization.
- End-to-end logging with rotation.
- Error handling and edge cases in real-world usage.

## Scenarios

| ID | Scenario | Description | Type |
| :--- | :--- | :--- | :--- |
| **CORE-E2E-001** | **Full Lifecycle** | Verify complete flow: Init → Bind → Log → Rotate → Verify Archive. | Positive |
| **CORE-E2E-002** | **Bind Twice** | Verify behavior when `bind()` is called multiple times on same instance. | Negative |
| **CORE-E2E-003** | **Corrupt Config** | Verify graceful handling when rotation config file is corrupted/invalid YAML. | Negative |
