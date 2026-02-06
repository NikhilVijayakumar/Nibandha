### 📂 `.agent\skills\nibandha-manager\resources\recovery_protocols.md`

# Nibandha Manager Recovery Protocols: The "Self-Healing" Manual

This document defines how the Nibandha Manager reacts when `scripts/check_foundations.py` or `scripts/nibandha_doctor.py` reports a failure.

---

## 🚨 Scenario 0: Environment Breach (Critical Gate)

**Detection:** The virtual environment `./.venv` is missing, or the manager detects execution via a global Python interpreter.

* **Instruction:** **Hard Stop.**
* **Action:** 1. Abort all agent handovers.
2. Log: `❌ CRITICAL: Environmental Sovereignty violated. Stage 0 Failure.`
3. **Instruction to User:** "Please run environment setup. Nibandha Manager cannot operate outside the locked .venv."

---

## 🛑 Scenario 1: Missing Artifacts (Chain Break)

**Detection:** A stage is reported as complete, but physical files (Blueprint, Tests, or Core Logic) are missing or empty.

* **Instruction:** **Rollback.**
* **Action:** 1. Do not proceed to the next agent.
2. Re-activate the *previous* agent.
3. Issue a **Defect Report**: "Required artifact `{file_path}` is missing. Re-generate the module following the Gold Standard."
* **Goal:** Synchronize the physical file system with the architectural state.

---

## ⚠️ Scenario 2: Validation Failure (Quality Gate)

**Detection:** Artifacts exist but violate standards (e.g., `print()` detected, relative imports found, or Pydantic models are not `frozen`).

* **Instruction:** **Demand Refactor.**
* **Action:**
1. **Do Not Fix:** The Manager must never attempt to edit the code itself.
2. **Log Capture:** Identify the specific violation (e.g., "Relative import found on line 5").
3. **Handback:** Return the error log to the implementing agent: "Implementation failed quality audit. Refactor to enforce Absolute Imports and Frozen Pydantic models."



---

## 🧪 Scenario 3: TDD Mismatch (ID Desync)

**Detection:** The `Clean-Implementation` logic lacks the Traceability IDs defined in the Blueprint.

* **Instruction:** **Traceability Alignment.**
* **Action:** 1. Compare `docs/test/` IDs with `src/{root}/{module}/` strings.
2. Point out missing IDs: "Traceability Gap: Scenario `AR-UT-005` is not logged in the core logic."
3. Require the agent to inject the missing `logger.info('[ID] ...')` calls.

---

## 🔄 Scenario 4: Context Overflow (Memory Reset)

**Detection:** Conversation length causes the agent to ignore the `NIBANDHA_ARCH.md` standards.

* **Instruction:** **State Refresh.**
* **Action:** 1. Re-read `resources/NIBANDHA_ARCH.md`.
2. Re-parse `pyproject.toml` to re-identify the absolute `{root}`.
3. Explicitly restate the 4-stage workflow (Stage 0 through 3).

---

