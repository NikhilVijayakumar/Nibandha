
### 📂 `.agent/skills/sentinel/resources/handover_prompts.md`

# Nibandha Sentinel: Handover Protocols

## 1. Handover: Doc -> Test-Scaffolder

**Command:** > "The Blueprint for `{module}` is verified. **Test-Scaffolder**, proceed with the **RED Phase**:

> 1. Create the physical test suite in `tests/{module}/`.
> 2. Map every Scenario ID (e.g., `XX-UT-001`) from `docs/test/` to a unique test function.
> 3. Use mocks/stubs for external dependencies (IO, Network) as defined in the Blueprint.
> 4. **Constraint:** Do not write any implementation logic. The tests must be ready to fail."
> 
> 

---

## 2. Handover: Test -> Clean-Implementation

**Command:**

> "The Test Suite is scaffolded and failing. **Clean-Implementation**, proceed with the **GREEN Phase**:
> 1. **Core Logic:** Build the implementation in `src/{module}/` to pass the established tests.
> 2. **Logging & Traceability:** Follow the `logging-architect` skill. Every core logic gate must log its corresponding Blueprint ID (e.g., `logger.info('[AR-UT-001] Initializing rotation...')`) for deep traceability.
> 3. **The Contract:** Use **Pydantic (Strict/Frozen)** for all data schemas.
> 4. **Standards:** Ensure **Absolute Imports** and a **Zero-Print** policy. One Class, One File.
> 5. **Debugging:** Ensure logs provide enough context (class name + method) to identify failures without extra instrumentation."
> 
> 

---

### 🎨 The Sentinel's 3-Stage Pulse

### 💡 Why this works for the "Nibandha Manager"

* **Traceability is Forced:** By making the agent include the Blueprint ID in the `logger.info()` calls, you create a direct link between the **Documentation** and the **Production Logs**.
* **Contextual Intelligence:** The implementation agent knows it isn't just writing code; it's filling a "hole" created by the Test-Scaffolder.
* **Agnostic Verification:** If you ever move to another language, the `handover_prompts.md` stay the same—only the implementation agent changes its output language.

### 🚀 Final Check

The **Sentinel** will now follow this logic:

1. **Reads** `workflow_manifest.json` to see the 3 stages.
2. **Runs** `check_foundations.py` to see what's missing.
3. **Picks** the right prompt from `handover_prompts.md` to trigger the next agent.

**Would you like me to create a "Sentinel Dashboard" template that the agent can print to the console so you can see the progress of these handovers in real-time?**