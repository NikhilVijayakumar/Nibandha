### 📂 `.agent/skills/sentinel/resources/recovery_protocols.md`

# Sentinel Recovery Protocols: The "Self-Healing" Manual

This document defines how the Sentinel must react when `check_foundations.py` or the `nibandha_doctor.py` reports a failure.

---

## 🛑 Scenario 1: Missing Artifacts (Chain Break)

**Detection:** A stage is marked "Complete" by an agent, but the physical files (Blueprint, Tests, or Core Logic) are missing or empty.

* **Instruction:** **Rollback.**
* **Action:** 1. Do not proceed to the next agent.
2. Re-activate the *previous* agent.
3. Issue a **"Defect Report"**: "Required artifact `{file_path}` is missing. Re-generate the module following the Gold Standard."
* **Goal:** Ensure the physical file system matches the architectural state before moving forward.

---

## ⚠️ Scenario 2: Validation Failure (Quality Gate)

**Detection:** Artifacts exist, but they violate Nibandha standards (e.g., `print()` detected, relative imports found, or Pydantic models are not `frozen`).

* **Instruction:** **Demand Refactor.**
* **Action:**
1. **Do Not Fix:** The Sentinel must never attempt to edit the code itself.
2. **Log Capture:** Capture the specific error (e.g., "Found print() on line 42").
3. **Handback:** Return the error log to the implementing agent: "Implementation failed quality audit. Refactor the code to remove prints and enforce absolute imports."



---

## 🧪 Scenario 3: TDD Mismatch (ID Desync)

**Detection:** The `Clean-Implementation` logic does not contain the Logging IDs defined in the `Test-Scaffolder` phase.

* **Instruction:** **Traceability Alignment.**
* **Action:** 1. Compare `docs/test/` IDs with `src/{module}/` strings.
2. Point out the missing IDs: "Traceability Gap: Scenario `AR-UT-005` is not logged in the core logic."
3. Require the agent to inject the missing `logger.info('[ID] ...')` calls.

---

## 🔄 Scenario 4: Context Overflow (Memory Reset)

**Detection:** The conversation length is causing the agent to lose track of the `NIBANDHA_ARCH.md` standards.

* **Instruction:** **State Refresh.**
* **Action:** 1. Re-read the `resources/NIBANDHA_ARCH.md` file.
2. Explicitly state the 3-stage workflow to "reset" the Sentinel's priority.

---
