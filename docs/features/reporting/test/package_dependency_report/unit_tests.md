# Package Dependency Report - Unit Tests

## Purpose
Verify parsing of pip output and status logic.

---

## Scenarios

### PD-UT-001: Parse Outdated JSON
**Description**: Correctly parses `pip list --outdated` JSON.
**Input**: JSON list of outdated pkgs.
**Expected**: List of `Package` objects with current/latest versions.

### PD-UT-002: Determine Status (Warn)
**Description**: Outdated packages exist, no vulns.
**Expected**: Status 🟡 WARN.

### PD-UT-003: Determine Status (Fail)
**Description**: Vulnerabilities detected.
**Expected**: Status 🔴 FAIL.

### PD-UT-004: Parse Vulnerability JSON
**Description**: Parse `pip-audit` output.
**Expected**: Extract CVE IDs and descriptions.

### PD-UT-005: Clean State
**Description**: No outdated, no vulns.
**Expected**: Status 🟢 PASS.
