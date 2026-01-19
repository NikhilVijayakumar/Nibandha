This is a crucial addition. By removing the "3 sub-module" mental trap, you allow the **Doc-Architect** to be truly data-driven based on the complexity of the task.

Here is the updated **Gold Standard** that explicitly codifies the **N-Component Scaling** rule.

---

### 📂 `examples/architectural_decisions.md`

# Architectural Decision Gold Standard

Use these examples to determine if a request requires **Functional Decomposition** or a **Main Module Only** focus.

> **Core Rule:** Decomposition into sub-modules is **adaptive**. There is no fixed number. A module can have **zero** sub-modules (Utility) or **** sub-modules (Complex System) based on logical boundaries.

---

## Case A: Zero Sub-modules ()

**Scenario:** "Add a UUID generation utility."

### 1. Decision Logic

* **Reason:** The task is a single, isolated functional unit.
* **Scaffolding:** No sub-folders.
* **Documentation:**
* `docs/modules/uuid.md`
* `docs/test/uuid/integration_scenarios.md` (Acting as the primary test doc).



---

## Case B: Variable Sub-modules ()

**Scenario:** "Add a Log Archiver with compression and cloud backup."

### 1. Decision Logic

* **Reason:** Multiple distinct side-effects (IO vs. Network vs. Logic).
* **Count:** The agent identifies exactly **3** components: `FileFinder`, `Compressor`, and `S3Uploader`.
* **Scaffolding:** 3 sub-folders in `docs/test/` + 1 `integration` folder.

---

## Case C: The Orchestrator Rule

**Whenever , an Integration Point is Mandatory.**

If you have even **one** sub-module, you must also document the **Integration Point** (The Orchestrator) to verify how that sub-module interacts with the main Nibandha entry point.

| Sub-module Count | Total Test Scenario Files | Breakdown |
| --- | --- | --- |
| **0** | 1 | `integration_scenarios.md` |
| **1** | 2 | `sub1_scenarios.md` + `integration_scenarios.md` |
| **3** | 4 | `sub1`, `sub2`, `sub3` + `integration_scenarios.md` |

---

### 💡 Agent Guidance: How to count 

Before running the scaffolding script, the **Doc-Architect** must answer:

1. **Atomic Units:** How many "unrelated" tasks are being performed? (e.g., "Filtering" is unrelated to "Disk Writing"). Each is a sub-module.
2. **Mocking Boundaries:** If I want to test the logic of Part A without running Part B, they must be separate sub-modules.
3. **Number Choice:** Select the **smallest ** that satisfies clean separation. **Do not invent components to reach a specific number.**

---
