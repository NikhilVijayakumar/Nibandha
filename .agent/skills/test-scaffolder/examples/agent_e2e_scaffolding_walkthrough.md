### 📂 `examples/agent_e2e_scaffolding_walkthrough.md`

# Agent Guide: E2E Scaffolding (Granular & Isolated)

This example shows the agent how to take the **Archiver** blueprint and generate the physical E2E test suite using the **** and **One-File-Per-ID** rules.

## 1. Input: The Blueprint (E2E Scenarios)

The agent reads `docs/test/archiver/e2e_scenarios.md`:

| ID | Scenario | Slug | Expected Outcome |
| --- | --- | --- | --- |
| **AR-E2E-001** | Full Archive Cycle | `full_cycle` | File compressed, moved, and logged. |
| **AR-E2E-005** | Quota Cleanup | `quota_cleanup` | Oldest logs deleted when 1GB reached. |

## 2. Agent Reasoning (E2E Logic)

1. **Target Directory:** `tests/e2e/archiver/integration/` (since these involve multiple sub-modules).
2. **Setup Requirement:** Must include the `nibandha_env` fixture to protect the host OS.
3. **Execution:** Create one file per E2E ID.

## 3. Physical Result (The Output)

### File A: `tests/e2e/archiver/integration/test_ar_e2e_001_full_cycle.py`

```python
"""
ID: AR-E2E-001
Description: Full Archive Cycle - End-to-End verification.
Linked Spec: docs/test/archiver/e2e_scenarios.md
"""
import pytest
from pathlib import Path

def test_ar_e2e_001_execution(nibandha_env):
    """
    TDD Marker: RED PHASE
    This test verifies the actual creation of a .zip file in the .Nibandha directory.
    """
    # 1. Setup: nibandha_env provides a clean /tmp/.Nibandha/ path
    # 2. Action: Run the archiver entry point
    # 3. Assert: Physical file existence and size
    
    assert False, "RED PHASE: [AR-E2E-001] Full cycle implementation not found."

```

### File B: `tests/e2e/archiver/integration/test_ar_e2e_005_quota_cleanup.py`

```python
"""
ID: AR-E2E-005
Description: Quota Cleanup - Verifies physical deletion of oldest files.
"""
import pytest
from pathlib import Path

def test_ar_e2e_005_cleanup_behavior(nibandha_env):
    # 1. Setup: Fill nibandha_env with 1.1GB of dummy files
    # 2. Action: Trigger Archiver check
    # 3. Assert: Oldest file is physically unlinked (os.remove)
    
    assert False, "RED PHASE: [AR-E2E-005] Cleanup logic not implemented."

```

---

## 💡 Why the Agent uses this E2E Gold Standard

* **Environment Safety:** By using the `nibandha_env` fixture in every file, the agent ensures that even if a "Delete All" bug exists in the implementation, it only affects the temporary folder.
* **Traceability at Scale:** In E2E tests, complexity is high. Having `test_ar_e2e_005_quota_cleanup.py` isolated makes it easy to see if a failure is due to a **Permission Error** or a **Logic Error**.
* **Clean State:** Pytest destroys and recreates the `nibandha_env` for *each* file, ensuring that the result of `AR-E2E-001` doesn't interfere with the quota check in `AR-E2E-005`.

---
