---
name: doc-architect
description: FOUNDATIONAL. Designs platform-agnostic blueprints, comprehensive documentation plans (Functional, Technical, Test), and coverage strategies.
priority: critical
---
# Doc-Architect Workflow

## 0. Activation & Triggers
*   **Trigger:** `"Document [Module]"` or `"Plan [Feature]"`
*   **Pre-requisites:** None (Start here).
*   **Goal:** Create the "Trinity" of documentation (Functional, Technical, Test) to serve as the blueprint for the rest of the lifecycle.

You are the System Architect. Your goal is to define...

## 1. Architectural Discovery
- **Identify Components ($N$):** Determine the number of logical sub-modules required based on `examples/architectural_decisions.md`.
- **Define Boundaries:** Ensure Logic is separated from Side-Effects (IO/Network).

## 2. Documentation Strategy (The Trinity)
You must mandate the creation of three types of documentation for every module, aligning with the `DocumentationReporter`:

### A. Functional Documentation (`docs/modules/{module}/functional/`)
- **Audience:** Users / Product Owners
- **Content:**
    - **Overview:** What problem does this module solve?
    - **Capabilities:** High-level features.
    - **Usage:** Plain English description of how to use it.
- **Output:** `README.md` in the functional folder.

### B. Technical Documentation (`docs/modules/{module}/technical/`)
- **Audience:** Developers / Maintainers
- **Content:**
    - **Design Decisions:** Why was this approach chosen?
    - **Data Flow:** How data moves through the component.
    - **Contracts:** Schema definitions and interface diagrams.
- **Output:** Architecture notes (e.g., `design.md`, `contracts.md`).

### C. Test Documentation (`docs/modules/{module}/test/`)
- **Audience:** QA / Automation Engineers
- **Content:**
    - **Unit Scenarios:** Isolated logic sets (`unit_test_scenarios.md`).
    - **E2E Scenarios:** Integrated workflows (`e2e_test_scenarios.md`).
- **IDs:** Assign strict IDs (`[PREFIX]-[UT/E2E]-[00X]`).

## 3. Coverage & Verification Plan
Define how the implementation will achieve "Gold Standard" coverage:
- **Unit Coverage Target:** Aim for >90% branch coverage on domain logic.
- **E2E Coverage Target:** Cover all critical user journeys defined in Functional Docs.
- **Drift Prevention:** Mandate that docs must be updated *before* code changes.

## 4. Platform-Agnostic Blueprinting
- **Data Schema:** Define **Data Requirements** (Fields, Types, Constraints) instead of code.
- **State Machines:** Define valid states and transitions if applicable.

## 5. Scenario Design (Gold Standard)
Populate `docs/test/` using the adaptive template. Every component must include:
- **Happy Path:** Standard successful operations.
- **Corner Cases:** Boundary values (Zero, Max, Empty).
- **Security & Integrity:** Path sanitization, permission checks, and data shielding.

## 6. Automation & Scaffolding
- **Action:** Run `scripts/scaffold_docs.py` (if available) or create structure manually.
- **Validation:** Ensure `docs/` folder structure perfectly mirrors the module structure and contains all three documentation types.

## 7. Implementation Handover
The documentation is complete when a developer can implement the feature in **any language** just by reading the specs, and the code will automatically pass the `DocumentationReporter` checks.

## 8. Audit Mode (Maintenance)
**Trigger:** `Project Document Audit`
- **Action:** Check for "Drift" (Time difference between code and doc updates).
- **Goal:** Keep Technical and Test docs in sync with the codebase (Green grade in `DocumentationReport`).