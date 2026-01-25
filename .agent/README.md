# Project Agent System

The **Project Agent System** is a portable, plug-and-play AI team that enforces "Gold Standard" quality in your Python project.

## 🚀 Quick Start (How to Use)

### 1. Installation
Copy this `.agent` folder to the root of your project. Ensure you have a `pyproject.toml`.

### 2. The Triggers (Command & Control)
Use these phrases to activate specific agents. The System will auto-detect your project structure.

| Agent | Trigger Phrase | What it does | Expected Outcome |
| :--- | :--- | :--- | :--- |
| **Quality Manager** | `"Act as Quality Manager"` | **Audit:** Runs `project_doctor.py` to check all modules. | Reports Pass/Fail for Docs, Tests, and Code. |
| **Doc Architect** | `"Document [Module]"` | **Plan:** Runs `scaffold_docs.py` to create the Trinity structure. | Creates `docs/modules/[Module]/functional/README.md` etc. |
| **Clean Impl.** | `"Implement [Module]"` | **Build:** References plans to write Pydantic/Clean Arch code. | Creates `src/[package]/[Module]/core.py` etc. |
| **Verifier** | `"Verify [Module]"` | **Test:** Runs tests and checks reports. | Returns `pytest` results and Coverage/Quality reports. |

### 3. Example Workflows (Copy-Paste Prompts)

#### A. Starting a New Feature
> "Act as Quality Manager. I need to create a new module called `archiver`. Please trigger the Doc Architect to scaffold the plan."

#### B. Auditing the System
> "Quality Manager, run a full system audit. Are there any relative imports or missing tests in the `rotation` module?"

#### C. Fixing Broken Code
> "I see the Quality Manager failed on `scheduler`. Please act as Clean Implementation agent and fix the relative imports to meet the standard."

## 🛠️ The Skills (Under the Hood)

*   **[Quality Manager](skills/quality-manager/SKILL.md)**: The State Machine. Enforces the loop.
*   **[Doc Architect](skills/doc-architect/SKILL.md)**: Ensures you plan before you build.
*   **[Clean Implementation](skills/clean-implementation.md)**: Writes generic, strict Python code.
*   **[Test Scaffolder](skills/test-scaffolder.md)**: Ensures TDD by creating failing tests first.

## 📂 Configuration (Rules)
*   **[Core Rules](rules/core-standards.md)**: Naming & Environment.
*   **[Testing](rules/testing-standards.md)**: `PREFIX-UT-001` mapping.
*   **[Imports](rules/import-standards.md)**: No relative imports.
