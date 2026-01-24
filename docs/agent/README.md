# Project Agent System Documentation

Welcome to the documentation for the **Project Agent System**. This directory contains detailed explanations of the agents (skills) and rules that govern this automated development ecosystem.

## 🧠 The Quality Manager
The system is orchestrated by the **Quality Manager**, a state-machine agent that ensures rigorous Quality Assurance practices are followed before any code is merged.

*   [**Quality Manager Spec**](skills/quality-manager.md)

## 🏗️ Core Skills
Detailed documentation for the specialized agents:

*   [**Doc Architect**](skills/doc-architect.md): How blueprints and trace IDs are generated.
*   [**Test Scaffolder**](skills/test-scaffolder.md): The logic behind TDD automation.
*   [**Clean Implementation**](skills/clean-implementation.md): Coding standards and architectural patterns.
*   [**Verification Manager**](skills/verification-manager.md): How reports are analyzed.

## 📜 Architectural Rules
The "Constitution" that the agents enforce:

*   [**Core Standards**](rules/core-standards.md): Naming, Layers, and Environment.
*   [**Testing Standards**](rules/testing-standards.md): Scenario-based testing rules.
*   [**Import Standards**](rules/import-standards.md): Absolute import enforcement.
*   [**Configuration Rules**](rules/config-enforcement.md): Pydantic + Non-interactive rules.

## 🚀 Usage
This documentation is intended for:
1.  **Developers**: To understand why an agent rejected their code.
2.  **Architects**: To customize the rules for specific project needs.
3.  **Newcomers**: To learn the "Gold Standard" way of working in this repository.
