### 📂 `.agent\skills\nibandha-manager\resources\handover_prompts.md`

# Nibandha Manager: Handover Protocols

## 1. Handover: Doc -> Test-Scaffolder

**Condition:** Stage 1 Blueprint verified via `./.venv/bin/python scripts/check_foundations.py`.

**Command:**

> "The Blueprint for `{module}` is verified. **Test-Scaffolder**, proceed with the **RED Phase**:
> 1. **Environment:** Use the local `./.venv` for all discovery.
> 2. **Structure:** Create the physical test suite in `tests/{module}/`.
> 3. **Mapping:** Map every Scenario ID (e.g., `XX-UT-001`) from the Blueprint to a unique test function.
> 4. **Mocks:** Use mocks/stubs for external dependencies (IO, Network) as defined.
> 5. **Constraint:** Do not write implementation logic. Tests must be ready to run and fail."
> 
> 

---

## 2. Handover: Test -> Clean-Implementation

**Condition:** Stage 2 Test Suite verified via `./.venv/bin/python scripts/check_foundations.py`.

**Command:**

> "The Test Suite is scaffolded. **Clean-Implementation**, proceed with the **GREEN Phase**:
> 1. **Pathing:** Identify Source Root from `pyproject.toml`. Implement in `src/{root}/{module}/`.
> 2. **Core Logic:** Build implementation to pass established tests.
> 3. **Logging:** Every logic gate MUST log its Blueprint ID (e.g., `logger.info('[AR-UT-001] ...')`).
> 4. **The Contract:** Use **Pydantic (Strict/Frozen)** for all data schemas.
> 5. **Standards:** Use **Absolute Imports** and **Zero-Print** policy. One Class, One File.
> 6. **Environment:** Ensure all code is validated using the local `./.venv` interpreter."
> 
> 

---

### 💡 Why this works for the "Nibandha Manager"

* **Environment Locking:** By injecting Stage 0 reminders into the prompts, the agents are reminded to use the `.venv` even after a handover.
* **Root Discovery:** The implementation prompt now forces the agent to check `pyproject.toml` for the `{root}` rather than assuming a generic `src/` path.
* **Traceability Link:** The handover explicitly commands the "Blueprint ID" logging, ensuring the **Logging-Architect** requirements are met during implementation.

---

