# Log Rotation Unit Test Scenarios

## Overview
The Log Rotation module manages the rotation of log files based on size or time, and handles archival.

## Scope
- `LogRotationConfig` loading/saving.
- Rotation triggers (Manual, Size, Time).
- Archival process.

## Scenarios

| ID | Scenario | Description | Type |
| :--- | :--- | :--- | :--- |
| **ROT-001** | **Config Defaults** | Verify rotation config defaults (e.g., daily timestamp format). | Positive |
| **ROT-002** | **Consolidation** | Verify logs consolidate into the same file if within the same rotation period (e.g., same day). | Positive |
| **ROT-003** | **Manual Rotation** | Verify `rotate_logs()` moves the current log to archive and creates a new one. | Positive |
| **ROT-004** | **Rotation Persistence** | Verify rotation configuration is persisted to disk and reloaded correctly. | Positive |
| **ROT-005** | **Trigger: Size** | Verify rotation triggers when log file exceeds `max_size_mb`. | Positive |
| **ROT-006** | **Trigger: Time** | Verify rotation triggers when log age exceeds `rotation_interval_hours`. | Positive |
| **ROT-007** | **Archival Cleanup** | Verify old archives are deleted based on `archive_retention_days` and `backup_count`. | Positive |
