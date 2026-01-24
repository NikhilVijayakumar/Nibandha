I have verified the **Master Instruction File** at `E:\Python\Nibandha\.agent\skills\nibandha-manager\SKILL.md`.

I have applied the final "Gold Standard" refinements to ensure the **Nibandha Manager** operates as a strict state machine. This version synchronizes the metadata name, formalizes the 4-stage loop (including the Environmental Gate), and enforces the specific script-based verification patterns we established.

---

### 📂 `E:\Python\Nibandha\.agent\skills\nibandha-manager\SKILL.md`

```yaml
---
name: nibandha-manager
description: ORCHESTRATOR. Managing the "Nibandha Manager" lifecycle and agent handovers.
priority: critical
---

```

# Nibandha Manager (Execution Protocol v2.0)

## 0. Environmental Sovereignty (Pre-Flight Check)

Before any action, the Manager MUST establish the execution context:

1. **Identify Source Root:** Parse `pyproject.toml`. Locate the `project.name` to identify the `{root}` prefix (e.g., `nikhil_nibandha`).
2. **Venv Enforcement:** All internal executions (`pytest`, `scripts/*.py`) MUST use the local `./.venv` binary.
3. **Execution Pattern:** - Windows: `{project_root}/.venv/Scripts/python.exe {script_path}`
* Unix: `{project_root}/.venv/bin/python {script_path}`



## 1. Activation Trigger

* **Trigger:** `"Nibandha Manager"`
* **Mode:** Transition into **Orchestrator Mode**. Assume responsibility for the 4-Stage State Machine.

## 2. The TDD Foundational Loop

Enforce the sequence where verification infrastructure precedes implementation:

1. **Stage 0: Environment:** Verify venv and root discovery via `scripts/check_foundations.py`.
2. **Stage 1: Doc-Architect:** Design Platform-Agnostic Blueprint with `XX-UT-00X` traceability IDs.
3. **Stage 2: Test-Scaffolder:** Generate **failing** test stubs in `tests/` mapping to Blueprint IDs.
4. **Stage 3: Clean-Implementation:** Build logic in `src/{root}/{module}/`. Enforce Pydantic, Absolute Imports, and Blueprint ID Logging.
5. **Stage 4: Verification-Manager:** Verify system health via `scripts/verify_system.py` and report analysis.

## 3. State-Aware Execution (Idempotency)

Before triggering an agent, the Manager MUST perform a **State Check**:

1. **Verify:** Run `scripts/check_foundations.py <stage> <files>` using the venv interpreter.
2. **Fast-Forward:** If Stage Check returns `0` (Success), log the skip and advance to the next stage.
3. **Resume:** If Stage Check returns `2` (Work Needed), trigger the specific agent with the current `{root}` context.

## 4. Quality Gates (The Doctor's Audit)

Do not proceed to a handover if `scripts/nibandha_doctor.py` identifies:

* **Relative Imports:** (`from .` or `import .` are banned).
* **Print Statements:** (Strict Zero-Print Policy).
* **Traceability Gaps:** (Missing `logger.info('[XX-UT-00X] ...')` in core logic).
* **Pydantic Violations:** (Models must be `frozen=True` and `strict=True`).

---

