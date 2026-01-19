To ensure the **Sentinel** remains efficient, we must update the **Resume Behavior** to follow your streamlined 3-stage process. This logic ensures that if you stop and restart, the agent doesn't waste time (or tokens) on documentation or testing if they already exist.

---

### 📂 `examples/sentinel_resume_behavior.md`

# Sentinel Orchestration: Resume & Fast-Forward Logic

The Sentinel is **State-Aware**. It checks for the existence of artifacts before calling an agent. This allows you to manually edit a blueprint or resume a failed implementation without starting over.

## Scenario A: Blueprint Manual Override

**User Action:** You manually edit the `docs/modules/auth/README.md` to add a new security constraint.
**Input:** `"Nibandha Manager, create a Auth"`

1. **Sentinel** calls `check_foundations.py` for **Stage 1 (Doc-Architect)**.
2. **Detection:** Documentation exists.
3. **Action:** Sentinel logs: `[STATE] Blueprint detected. Respecting manual changes. Fast-forwarding to Stage 2.`
4. **Result:** Moves straight to **Test-Scaffolder**.

---

## Scenario B: Implementation Recovery

**User Action:** The implementation failed because of a network timeout.
**Input:** `"Nibandha Manager, create a Auth"`

1. **Sentinel** checks **Stage 1 (Docs)**  **EXISTS**.
2. **Sentinel** checks **Stage 2 (Tests)**  **EXISTS**.
3. **Detection:** `src/auth/core.py` is missing or empty.
4. **Action:** Sentinel logs: `[STATE] Docs and Tests verified. Resuming at Stage 3: Clean-Implementation.`
5. **Result:** Only the implementation agent is triggered.

---

## Scenario C: The "Hard Reset"

**User Action:** You want to start completely from scratch.
**Input:** `"Nibandha Manager, reset and create a Auth"` (or manually delete the folders).

1. **Sentinel** detects missing `docs/`.
2. **Action:** Triggers the **Full Foundational Loop** (Stage 1  2  3).

---

### 💡 The "Resume" Logic Table

| Stage | Artifact Target | Sentinel Action if Exists |
| --- | --- | --- |
| **1. Doc-Architect** | `docs/modules/{module}/README.md` | **SKIP** & Log: "Blueprint Verified" |
| **2. Test-Scaffolder** | `tests/{module}/test_integration.py` | **SKIP** & Log: "Test Suite Verified" |
| **3. Clean-Impl** | `src/{module}/core.py` | **VERIFY** (Check for Absolute Imports/Pydantic) |
