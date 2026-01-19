# Package Dependency Report - Data Builder

## Overview
The `PackageDependencyDataBuilder` interacts with package management tools (`pip`) to gather metadata about installed packages.

---

## Analysis Logic

### 1. Inventory
- Command: `pip list --format=json`
- Output: List of installed packages and current versions.

### 2. Outdated Check
- Command: `pip list --outdated --format=json`
- Output: Packages with newer versions available.

### 3. Vulnerability Audit (Optional/Future)
- Command: `pip-audit -f json`
- Output: Known CVEs for installed versions.

---

## Output Data Schema (`package_dependency_data.json`)

```json
{
  "date": "2026-01-17",
  "status": "🟡 WARN",
  
  "summary": {
    "total_packages": 24,
    "outdated": 3,
    "vulnerable": 0
  },

  "outdated_packages": [
    {
      "name": "pandas",
      "current": "1.3.0",
      "latest": "1.4.0",
      "type": "wheel"
    }
  ],

  "vulnerabilities": [],

  "all_packages_table": "| Package | Version | ...",
  "outdated_table": "| Package | Current | Latest | ..."
}
```

## Status Determination
- **🔴 FAIL**: Vulnerabilities found.
- **🟡 WARN**: Outdated packages found.
- **🟢 PASS**: All up-to-date and secure.
