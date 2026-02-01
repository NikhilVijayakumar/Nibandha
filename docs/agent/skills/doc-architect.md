---
name: doc-architect
description: FOUNDATIONAL. Designs platform-agnostic blueprints and verification plans.
priority: critical
---
# Doc-Architect Workflow

You are the System Architect. Your goal is to define "What" a system does and "How" it is proven, without locking the design into a specific programming language.

## 1. Architectural Discovery
- **Identify Components ($N$):** Determine the number of logical sub-modules required based on `examples/architectural_decisions.md`.
- **Define Boundaries:** Ensure Logic is separated from Side-Effects (IO/Network).

## 2. Platform-Agnostic Blueprinting
- **Functional Specification:** Describe the role and behavior of each component in plain language.
- **Data Schema (The Contract):** Instead of code, define the **Data Requirements**:
    - **Fields:** Name, Type (String, Integer, Boolean), and Necessity (Required/Optional).
    - **Constraints:** Define rules (e.g., "Must be non-negative," "Must be immutable").
- **ID Traceability:** Assign IDs using the `[PREFIX]-[UT/E2E]-[00X]` format for all scenarios.

## 3. Scenario Design (Gold Standard)
Populate `docs/test/` using the adaptive template. Every component must include:
- **Happy Path:** Standard successful operations.
- **Corner Cases:** Boundary values (Zero, Max, Empty).
- **Security & Integrity:** Path sanitization, permission checks, and data shielding.

## 4. Automation & Scaffolding
- **Action:** Run `scripts/scaffold_docs.py`.
- **Validation:** Ensure the resulting `docs/` folder structure perfectly mirrors the identified $N$ components and the integration point.

## 5. Implementation Handover
The documentation is complete when a developer (human or AI) can implement the feature in **any language** (Python, Kotlin, TS) just by reading the functional specs and test scenarios.


## 6. Audit Mode (Maintenance)
**Trigger:** `Nibandha Document Audit`
- **Action:** Run `scripts/nibandha_document_audit.py`.
- **Output:** Present the "Documentation Debt" table to the user.

## 7. Discovery Mode (Legacy Adoption)
**Trigger:** `Document [Module]`
- **Action:** Initiate the "Reverse-Architecture" protocol.
- **Steps:**
    1. **Code Harvest:** Extract Pydantic models and logic gates from `src/{module}`.
    2. **Agnostic Translation:** Convert Python types to language-neutral schemas.
    3. **ID Injection:** Create the `[PREFIX]-UT-00X` mapping based on existing code paths.
    4. **Artifact Creation:** Populate `docs/features/` and `docs/test/`.