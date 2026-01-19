# Logging Module Unit Test Scenarios

## Overview
The Logging module ensures correct handler attachment, log levels, and separation of logs between different applications.

## Scope
- Handler types (File, Stream).
- Handler attachment to specific loggers (not Root).
- Log propagation settings.
- Log file content verification.

## Scenarios

| ID | Scenario | Description | Type |
| :--- | :--- | :--- | :--- |
| **LOG-001** | **Handler Attachment** | Verify handlers are attached to the named logger (`<AppName>`) and not the root logger. | Positive |
| **LOG-002** | **Propagation Check** | Verify `propagate` is set to `False` to prevent log doubling. | Positive |
| **LOG-003** | **Content Verification** | Verify logs are written to the correct file in `logs/data`. | Positive |
| **LOG-004** | **Child Logger** | Verify child loggers (e.g., `AppName.module`) inherit handlers/write to the same file. | Positive |
| **LOG-005** | **Timestamp Default** | Verify default timestamp format is daily (`%Y-%m-%d`). | Positive |
| **LOG-006** | **Daily Consolidation** | Verify logs consolidate into the same file if restarted within the same rotation period. | Positive |
