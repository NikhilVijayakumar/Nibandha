# Project Agent System Documentation

The **Project Agent System** is a managed ecosystem of specialized AI agents (skills) orchestrated by the **Quality Manager**. This guide explains how to use the system to build software that meets the "Gold Standard".

## 🚀 Quick Start

### 1. The Triggers (Command & Control)
Use these phrases to activate specific agents. The System will auto-detect your project structure.

| Agent | Trigger Phrase | What it does | Expected Outcome |
| :--- | :--- | :--- | :--- |
| **Quality Manager** | `"Act as Quality Manager"` | **Audit:** Runs `project_doctor.py` to check all modules. | Reports Pass/Fail for Docs, Tests, and Code. |
| **Doc Architect** | `"Document [Module]"` | **Plan:** Runs `scaffold_docs.py` to create the Trinity structure. | Creates `docs/modules/[Module]/functional/README.md` etc. |
| **Clean Impl.** | `"Implement [Module]"` | **Build:** References plans to write Pydantic/Clean Arch code. | Creates `src/[package]/[Module]/core.py` etc. |
| **Verifier** | `"Verify [Module]"` | **Test:** Runs tests and checks reports. | Returns `pytest` results and Coverage/Quality reports. |

### 2. Example Workflows

#### A. Starting a New Feature
> "Act as Quality Manager. I need to create a new module called `archiver`. Please trigger the Doc Architect to scaffold the plan."

#### B. Auditing the System
> "Quality Manager, run a full system audit. Are there any relative imports or missing tests in the `rotation` module?"

## 🧠 The Skills (Deep Dive)

*   [**Verification Manager**](skills/verification-manager.md): How reports (Unit, E2E, Arch, Complexity, etc.) are analyzed.
*   [**Quality Manager Spec**](skills/quality-manager.md): The State Machine logic.
*   [**Doc Architect**](skills/doc-architect.md): How blueprints and ids are generated.
*   [**Clean Implementation**](skills/clean-implementation.md): Coding standards and Pydantic rules.
*   [**Test Scaffolder**](skills/test-scaffolder.md): TDD automation strategies.

## 📜 Architectural Rules
The "Constitution" that the agents enforce:

*   [**Core Standards**](rules/core-standards.md): Naming, Layers, and Environment.
*   [**Testing Standards**](rules/testing-standards.md): Scenario-based testing rules.
*   [**Import Standards**](rules/import-standards.md): Absolute import enforcement.
*   [**Configuration Rules**](rules/config-enforcement.md): Pydantic + Non-interactive rules.

This system ensures that if you follow the triggers, your code is **Publication-Ready by Default**.
