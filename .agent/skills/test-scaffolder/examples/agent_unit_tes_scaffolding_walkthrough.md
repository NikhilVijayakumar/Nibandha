### 📂 `examples/agent_scaffolding_walkthrough.md`

# Agent Guide: From Blueprint to Physical Test Files

This example demonstrates how the **Test-Scaffolder** agent interprets the `unit_test_scenarios.md` and applies the `scaffold_tests.py` logic to create granular, ID-linked files.

## 1. Input: The Blueprint (Snippet)

The agent reads `docs/test/archiver/unit_test_scenarios.md`:

| ID | Scenario | Slug |
| --- | --- | --- |
| **AR-UT-007** | Path Traversal Shield | `path_traversal` |
| **AR-UT-001** | Standard Compression | `compression` |

## 2. Agent Reasoning (Logic Flow)

Instead of a single `test_unit.py`, the agent must iterate through every row in the table:

1. **Target Directory:** `tests/unit/archiver/core/`
2. **Filename Construction:** `test_{id}_{slug}.py`
3. **Execution:** Call the internal `create_test_stub` logic for *each* ID.

## 3. Physical Result (The Output)

The agent executes the scaffolding logic, resulting in these distinct files:

### File A: `tests/unit/archiver/core/test_ar_ut_007_path_traversal.py`

```python
"""
ID: AR-UT-007
Description: Path Traversal Shield - Auto-generated TDD stub
Linked Spec: docs/test/archiver/unit_test_scenarios.md
"""
import pytest
from pathlib import Path

def test_ar_ut_007_logic():
    """TDD Marker: RED PHASE"""
    # This ID must be implemented in src/archiver/core.py with a matching log entry
    assert False, "RED PHASE: [AR-UT-007] Path Traversal Shield pending implementation"

```

### File B: `tests/unit/archiver/core/test_ar_ut_001_compression.py`

```python
"""
ID: AR-UT-001
Description: Standard Compression - Auto-generated TDD stub
"""
import pytest
from pathlib import Path

def test_ar_ut_001_logic():
    assert False, "RED PHASE: [AR-UT-001] Standard Compression logic pending"

```

---

## 4. Why the Agent follows this "Gold Standard"

* **Granularity:** If the implementation for `AR-UT-001` is finished, its specific test can be turned "Green" while `AR-UT-007` remains "Red."
* **Traceability:** The **Sentinel** can run `validate_traceability.py` and see exactly which file matches which requirement ID.
* **No File Bloat:** By keeping one scenario per file, the agent avoids "context drift" when debugging complex modules.

### 💡 Agent Tip

When you see a table in the documentation, your goal is to ensure the **Test Folder** becomes a mirrored physical representation of that table. If there are 11 rows, there must be 11 test files.

---

**Would you like me to update the `scaffold_tests.py` script to accept a JSON list of IDs so the agent can automate this 1-file-per-ID generation in a single command?**