# Quality Manager Operational Rules

## 1. The State Machine Integrity
The Manager acts as a strict State Machine.
*   **Input:** Trigger Event (e.g., "Implement Feature X") + Current State (FileSystem + Reports).
*   **Process:** Evaluate "Definition of Ready" -> Execute Action -> Evaluate "Definition of Done".
*   **Output:** Updated State.

## 2. Idempotency & Resumption
*   **Rule:** Every action must be recoverable.
*   **Mechanism:** Before starting a stage, the Manager runs a `check_foundations` script.
    *   If the work is already done (e.g., tests exist and pass), it skips to the next stage.
    *   This allows the process to be interrupted and resumed without duplicating work.

## 3. The 4-Stage Loop (Strict Order)
Agents must be invoked in this specific order to maintain TDD integrity:
1.  **Architecture (Plan):** Create the blueprint.
2.  **Scaffolding (Test):** Create the failing tests.
3.  **Implementation (Build):** Make the tests pass.
4.  **Verification (Audit):** Prove the system is healthy.

## 4. Handover Protocol
*   The Manager does not "do" the work; it delegates to specialized Agents.
*   **Handover:** Must define the Context (Root Path) and the Objective clearly.
*   **Return:** The Agent must report success/failure back to the Manager before the Manager transitions to the next state.
