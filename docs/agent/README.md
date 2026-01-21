# Antigravity User Guide 🚀

This guide explains how to use the specific **Agents (Skills)** installed in this workspace to automate your development workflow.

## 🎯 Quick Reference

| **I want to...** | **Use Agent...** | **Trigger Command** |
| :--- | :--- | :--- |
| **Start a new feature** | `Nibandha Manager` | `"Nibandha Manager, create [Feature Name]"` |
| **Design a new system** | `Doc-Architect` | `"Design [Module Name]"` |
| **Document existing code** | `Doc-Architect` | `"Document [Module]"` or `"Reverse engineer [File]"` |
| **Generate Tests** | `Test-Scaffolder` | `"Scaffold tests for [Module]"` |
| **Write Code** | `Clean-Implementation` | `"Implement [Module]"` |
| **Fix Bad Code** | `Refactor-Agent` | `"Refactor [File/Module]"` |
| **Check Security** | `Security & Pitfalls` | `"Audit [File]"` or `"Security check"` |
| **Release/Publish** | `Package-Maintainer` | `"Publish [Module]"` |

---

## 🤖 Detailed Agent Guide

### 1. Nibandha Manager (The Project Lead)
**"The All-in-One Orchestrator"**

*   **How it helps:** Instead of manually running 4 different steps (Plan → Test → Code → Verify), the Manager handles the entire loop for you. It ensures you never skip a step.
*   **When to use:** When you are starting a **new module**, **feature**, or **service** from scratch.
*   **Trigger:**
    > "Nibandha Manager, create the `UserAuth` module."
*   **What happens:**
    1.  Checks your environment (`.venv`, dependencies).
    2.  Creates a Design Blueprint (via `Doc-Architect`).
    3.  Creates Failing Tests (via `Test-Scaffolder`).
    4.  Writes the Code (via `Clean-Implementation`).
    5.  Verifies everything passes.

### 2. Doc-Architect (The Designer)
**"The Blueprint Maker"**

*   **How it helps:** Prevents "coding in the dark." It forces you to think about data structures and edge cases *before* writing code. It generates standard `docs/modules/.../README.md` files.
*   **When to use:** When you have an idea but no concrete plan, or when you need to document legacy code.
*   **Trigger:**
    > "Design the `PaymentService`."
    > "Document the code in `src/core/legacy.py`."

### 3. Test-Scaffolder (The QA Engineer)
**"The TDD Enforcer"**

*   **How it helps:** Ensures you have 100% test coverage readiness. It creates "Red" (failing) tests based on strict requirements, forcing the implementation to be correct.
*   **When to use:** When you have a design or requirements but no tests.
*   **Trigger:**
    > "Scaffold tests for the `OrderProcessing` module."
    > "Generate unit tests for `utils.py`."

### 4. Clean-Implementation (The Senior Dev)
**"The Code Writer"**

*   **How it helps:** Writes rigorous, Clean Architecture-compliant code. It uses Pydantic for validation, Protocols for interfaces, and Dependency Injection by default.
*   **When to use:** When you have tests (or a clear plan) and need the actual Python implementation.
*   **Trigger:**
    > "Implement the `OrderService`."
    > "Write the code for `login_flow`."

### 5. Refactor-Agent (The Fixer)
**"The Tech Debt Crusher"**

*   **How it helps:** Identifies "Smelly" code (complex functions, circular dependencies) and fixes them without breaking functionality. It reads Quality Reports to find issues.
*   **When to use:** When a file is too long, hard to read, or when you get a "Complexity High" warning.
*   **Trigger:**
    > "Refactor `core/god_class.py` to be smaller."
    > "Fix the circular dependency in `auth`."

### 6. Package-Maintainer (The Librarian)
**"The API Guardian"**

*   **How it helps:** Manages the boring parts of Python packaging: `__init__.py` exports, `pyproject.toml` dependencies, and version bumping.
*   **When to use:** When you want to expose a class to other modules or prepare a library for release.
*   **Trigger:**
    > "Export `User` class from `domain`."
    > "Prepare `logging` module for release."

### 7. Security & Pitfalls (The Auditor)
**"The Safety Net"**

*   **How it helps:** Catches silent bugs and security holes that linters miss (e.g., `shell=True`, mutable defaults, hardcoded secrets).
*   **When to use:** Before committing code or when reviewing unknown code.
*   **Trigger:**
    > "Audit `infrastructure/shell_utils.py`."
    > "Check for security pitfalls in this file."

---

## 📜 Architectural Rules (The System Context)

These are **passive constraints**. You don't "trigger" them; they are always active. Use this list to understand *why* the Agent acts the way it does.

*   **Nibandha Core**: "Why did it create a Protocol?" -> Because the core rule mandates Dependency Inversion.
*   **Python Env**: "Why did it check my `.venv`?" -> Because the environment rule mandates virtual environments.
*   **Logging Standards**: "Why did it remove my `print()`?" -> Because the logging rule allows only `logger`.
*   **Testing**: "Why did it ask for E2E tests?" -> Because the testing rule requires 2 levels of verification.

To modify these behaviors, edit the files in `docs/agent/rules/`.
