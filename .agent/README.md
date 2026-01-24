# Nibandha Agent System

The **Nibandha Agent System** is a managed ecosystem of specialized AI agents (skills) orchestrated by the **Nibandha Manager**.

## 🧠 Nibandha Manager (The Orchestrator)

The **Nibandha Manager** ([Skill Definition](skills/nibandha-manager/SKILL.md)) is the central authority responsible for the software development lifecycle. It operates as a strict state machine, enforcing:

1.  **Environmental Sovereignty**: All actions occur within the defined project root and virtual environment.
2.  **TDD Foundational Loop**: A strict sequence of `Plan -> Test -> Implement -> Verify`.
3.  **Quality Gates**: Automated checks preventing bad code from progressing.

## 🛠️ Skills Ecosystem

Each skill is a specialized agent capability with its own **Instructions**, **Examples**, **Resources**, and **Scripts**.

### Core Lifecycle Skills
| Stage | Skill | Description |
| :--- | :--- | :--- |
| **0. Init** | **[Nibandha Manager](skills/nibandha-manager/SKILL.md)** | Orchestrates the lifecycle and manages handovers. |
| **1. Plan** | **[Doc Architect](skills/doc-architect/SKILL.md)** | Designs implementation blueprints and verification plans. |
| **2. Test** | **[Test Scaffolder](skills/test-scaffolder/SKILL.md)** | Generates failing tests based on blueprints. |
| **3. Build** | **[Clean Implementation](skills/clean-implementation/SKILL.md)** | Implements logic using Clean Architecture & Pydantic. |
| **4. Verify** | **[Verification Manager](skills/verification-manager/SKILL.md)** | Verifies system health via automated reports. |

### Support Skills
*   **[Logging Architect](skills/logging-architect/SKILL.md)**: Enforces structured logging standards.
*   **[Package Maintainer](skills/package-maintainer/SKILL.md)**: Manages dependencies and public API.
*   **[Refactor Agent](skills/refactor-agent/SKILL.md)**: Resolves technical debt and complexity.
*   **[Security & Pitfalls](skills/security-and-pitfalls/SKILL.md)**: Scans for vulnerabilities.

## 📂 Structure

The configuration is stored in `.agent/`:

*   `rules/`: Global rules applied to all agents.
*   `skills/`: actionable capability packages.
    *   `[skill-name]/`:
        *   `SKILL.md`: Master instructions.
        *   `examples/`: Reference interactions.
        *   `resources/`: Templates and assets.
        *   `scripts/`: Automation tools.

