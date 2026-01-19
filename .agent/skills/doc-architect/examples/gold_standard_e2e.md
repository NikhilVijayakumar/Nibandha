### 📂 `examples/gold_standard_e2e.md`

# E2E Test Scenarios: Archiver System

**Prefix:** `AR` | **Location:** `docs/test/archiver/e2e_test_scenarios.md`

## 1. Positive Flow (The Happy Path)

Verifies that the system performs its primary mission on a real disk structure.

| ID | Scenario | Verification Method | Expected Outcome |
| --- | --- | --- | --- |
| **AR-E2E-001** | **Standard Archival** | Check `.Nibandha/logs/archive/` | A valid `.zip` file exists containing the original log data. |
| **AR-E2E-002** | **Directory Scaffolding** | Run on fresh install | Module automatically creates missing `archive/` and `data/` folders. |
| **AR-E2E-003** | **Retention Purge** | Count files in archive dir | Total archives do not exceed `max_retention_count` after a new run. |

## 2. Negative Flow (Resilience)

Verifies how the system handles environmental failures without crashing.

| ID | Scenario | Verification Method | Expected Outcome |
| --- | --- | --- | --- |
| **AR-E2E-004** | **Permission Denied** | Set folder to `Read-Only` | Logger captures `OSError`; system skips archival instead of crashing. |
| **AR-E2E-005** | **Disk Full** | Simulate 0 bytes available | Archival is aborted; original log files remain intact (Atomic Safety). |
| **AR-E2E-006** | **Interrupted Stream** | Force-kill process mid-zip | On restart, system cleans up the partial `.zip.tmp` file. |

## 3. Security & Edge Cases

Verifies that the system protects the host OS from malicious or unexpected file states.

| ID | Scenario | Verification Method | Expected Outcome |
| --- | --- | --- | --- |
| **AR-E2E-007** | **Symlink Loop** | Create circular symlink | System detects loop or skips symlink; does not enter infinite recursion. |
| **AR-E2E-008** | **Non-Standard Chars** | Log name: `log_!@#$%^&*().log` | System handles filename correctly or sanitizes for zip compatibility. |
| **AR-E2E-009** | **Hidden Files** | Place `.hidden_log` in data dir | System ignores files starting with `.` (Default Library Behavior). |

---

### 💡 Why this is the "Gold Standard"

* **Verification Method:** Unlike unit tests (which check "Returns True"), E2E tests check **State Changes** (e.g., "Check File Count").
* **Atomic Safety:** Scenario `AR-E2E-005` ensures that if zipping fails, we don't delete the original logs. This is a critical library requirement.
* **Self-Healing:** Scenario `AR-E2E-006` proves the system can clean up its own garbage (temporary files) after a crash.
* **OS Independence:** These scenarios ensure the code works on Windows, Linux, and macOS by testing path handling and permissions.

### 🚀 Next Step

I have now provided the **Resource Template**, the **Complex Module Spec**, and both **Unit/E2E Scenarios**.
