# Logging Module E2E Test Scenarios

## Overview
Verify logging behavior in a real integrated environment.

## Scenarios

### Positive Cases
| ID | Scenario | Description |
| :--- | :--- | :--- |
| **LOG-E2E-001** | **Multi-Module Consolidation** | Logs from `App.ModuleA` and `App.ModuleB` should appear in `App.log` interleaved correctly. |
| **LOG-E2E-002** | **Startup Rotation** | Restart app with existing logs. Verify old log is archived and new log created. |

### Negative Cases
| ID | Scenario | Description |
| :--- | :--- | :--- |
| **LOG-E2E-003** | **Disk Full** | *Manual/Simulated:* Verify behavior when disk is full (should not crash app). |
| **LOG-E2E-004** | **Deleted Log File** | Delete active log file while app is running. Verify logger behavior (recreate or fail silent). |

### Corner Cases
| ID | Scenario | Description |
| :--- | :--- | :--- |
| **LOG-E2E-005** | **Binary Data Logging** | Log raw bytes or binary string. Verify safe persistence. |
