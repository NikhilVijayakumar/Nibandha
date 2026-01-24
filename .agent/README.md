# Project Agent System

The **Project Agent System** is a managed ecosystem of specialized AI agents (skills) orchestrated by the **Quality Manager**. It is designed to be a portable, generalized framework that can be dropped into any Python project to enforce "Gold Standard" quality.

## 🧠 Quality Manager (The Orchestrator)

The **Quality Manager** ([Skill Definition](skills/quality-manager/SKILL.md)) is the central authority responsible for the software development lifecycle. It operates as a strict state machine, enforcing:

1.  **Environmental Sovereignty**: All actions occur within the defined project root and virtual environment (`.venv`).
2.  **TDD Foundational Loop**: A strict sequence of `Plan -> Test -> Implement -> Verify`.
3.  **Quality Gates**: Automated checks preventing bad code from progressing.

## 🛠️ Skills Ecosystem

Each skill is a specialized agent capability with its own **Instructions**, **Examples**, **Resources**, and **Scripts**. The scripts are designed to auto-adapt to your project's naming conventions.

### Core Lifecycle Skills
| Stage | Skill | Description |
| :--- | :--- | :--- |
| **0. Init** | **[Quality Manager](skills/quality-manager/SKILL.md)** | Orchestrates the lifecycle and manages handovers. |
| **1. Plan** | **[Doc Architect](skills/doc-architect/SKILL.md)** | Designs platform-agnostic blueprints (Functional/Technical/Test). |
| **2. Test** | **[Test Scaffolder](skills/test-scaffolder/SKILL.md)** | Generates failing tests based on documented scenario IDs. |
| **3. Build** | **[Clean Implementation](skills/clean-implementation/SKILL.md)** | Implements logic using Clean Architecture & Pydantic. |
| **4. Verify** | **[Verification Manager](skills/verification-manager/SKILL.md)** | Verifies system health via automated reports. |

### Support Skills
*   **[Logging Architect](skills/logging-architect/SKILL.md)**: Enforces structured logging standards.
*   **[Package Maintainer](skills/package-maintainer/SKILL.md)**: Manages dependencies and public API.
*   **[Refactor Agent](skills/refactor-agent/SKILL.md)**: Resolves technical debt and complexity.
*   **[Security & Pitfalls](skills/security-and-pitfalls/SKILL.md)**: Scans for vulnerabilities.

## 📂 Architecture

The configuration is stored in `.agent/` and is fully self-contained:

*   `rules/`: Global rules (`core`, `testing`, `imports`) applied to all agents.
*   `skills/`: Actionable capability packages.
    *   `[skill-name]/`:
        *   `SKILL.md`: Master instructions (genericized).
        *   `examples/`: Reference interactions (using generic placeholders).
        *   `resources/`: Templates and assets.
        *   `scripts/`: Project-agnostic automation tools.

## 🚀 How to Use

1.  **Drop-in**: Copy the `.agent/` folder to your project root.
2.  **Configure**: Ensure you have a valid `pyproject.toml` (the agents use this to detect your package name).
3.  **Trigger**:
    *   **Start**: Tell the AI to ACT as the `"Quality Manager"`.
    *   **Specific Task**: Use triggers like `"Document [Module]"` (Doc Architect) or `"Implement [Module]"` (Clean Implementation).

The agents will automatically align with your project's structure and enforce strict quality standards from day one.
