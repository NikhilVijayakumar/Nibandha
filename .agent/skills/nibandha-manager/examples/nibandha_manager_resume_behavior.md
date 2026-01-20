### 📂 `.agent\skills\nibandha-manager\examples\nibandha_manager_resume_behavior.md`

# Nibandha Manager Orchestration: Resume & Fast-Forward Logic

The Nibandha Manager is **State-Aware** and **Environment-Locked**. It checks for the existence of the virtual environment and project artifacts before activating any agent. This prevents "Ghost Executions" and respects manual architectural overrides.

## 🔴 Stage 0: Environmental Sovereignty (The Hard Gate)

Before evaluating any resume scenario, the Manager performs the **Venv & Root Check**.

* **Venv Check:** Verify `./.venv/bin/python` (or `Scripts/python.exe`) exists.
* **Source Discovery:** Parse `pyproject.toml` to identify the absolute `{root}` (e.g., `nikhil/nibandha`).
* **Execution Pattern:** All foundation checks MUST use: `{project_root}/.venv/bin/python scripts/check_foundations.py`.

---

## Scenario A: Blueprint Manual Override

**User Action:** You manually edit `docs/modules/auth/README.md` to add custom logic.
**Input:** `"Nibandha Manager, create Auth"`

1. **Manager** verifies **Stage 0 (Venv)** -> **PASS**.
2. **Manager** calls `check_foundations.py` for **Stage 1 (Doc-Architect)**.
3. **Detection:** Documentation exists and is non-empty.
4. **Action:** Manager logs: `[STATE] Blueprint detected. Respecting manual changes. Fast-forwarding to Stage 2.`
5. **Result:** Moves straight to **Test-Scaffolder**.

## Scenario B: Implementation Recovery

**User Action:** Implementation failed mid-way or crashed.
**Input:** `"Nibandha Manager, create Auth"`

1. **Manager** verifies **Stage 0 (Venv)** -> **PASS**.
2. **Manager** checks Stage 1 (Docs) and Stage 2 (Tests) -> **BOTH EXIST**.
3. **Detection:** Target logic at `src/{root}/auth/core.py` is missing or fails quality gates.
4. **Action:** Manager logs: `[STATE] Docs and Tests verified. Resuming at Stage 3: Clean-Implementation.`

---

## 💡 The "Resume" Logic Table

| Stage | Artifact Target | Sentinel Check | Action if Valid |
| --- | --- | --- | --- |
| **0. Environment** | `./.venv/` | **Venv Enforcement** | **PROCEED** (Use `.venv` binary) |
| **1. Doc-Architect** | `docs/modules/{module}/README.md` | Existence & Size | **SKIP** (Log: "Blueprint Verified") |
| **2. Test-Scaffolder** | `tests/{module}/test_unit.py` | Existence & Size | **SKIP** (Log: "Test Suite Verified") |
| **3. Clean-Impl** | `src/{root}/{module}/core.py` | Import/Pydantic Check | **VERIFY** (Proceed if invalid) |

**Note:** If triggered with the keyword **"reset"**, the Manager ignores existing artifacts and overwrites all stages.

---
