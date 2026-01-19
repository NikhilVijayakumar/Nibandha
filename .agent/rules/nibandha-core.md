# Nibandha Core Architectural Rules

## 🏷️ Naming Strategy
- **Project Identity:** The project codename is **Nibandha** (Sanskrit for "binding"). Always refer to the overall system and its data root as Nibandha.
- **Module Naming:** All internal Python modules, classes, and variables must be named in **Plain English**. 
  - *Correct:* `src/nibandha/logging`, `src/nibandha/storage`, `class ReportGenerator`.
  - *Incorrect:* `src/nibandha/lekhanam`, `class Suvaidika`.
- **Directory Root:** The central data store must always be named `.Nibandha/`.

## 🏗️ Architectural Principles (Android-to-Python Clean)
- **Protocol-First Design:** Before implementing a feature, define a Python `Protocol` (interface). The implementation should be a separate class that satisfies this protocol.
- **Layer Separation:**
  - **Core/Domain:** Logic must be pure Python with zero dependencies on external storage or logging frameworks.
  - **Infrastructure:** All IO, file system, and logging implementation details go here.
- **Dependency Inversion:** Higher-level modules (like the `Nibandha` class) should depend on abstractions (Protocols), not concrete infrastructure classes.

## 🐍 Environment & Dependency Management
- **Python Interpreter:** Always use the virtual environment located at `./.venv`. Execute all commands (pytest, pip, etc.) using the binaries within this directory.
- **Dependency Source of Truth:** `pyproject.toml` is the master file. 
  - When adding dependencies, update `pyproject.toml` first.
  - Do not use global `pip install` commands.
- **Source Root:** Refer to `pyproject.toml` to identify the source directory. Do not assume a default `src/` layout unless specified in the config.

## 📁 File System & Logging
- **The Unified Root:** Every application (client) must have its own isolated folder within `.Nibandha/{App_Name}/`.
- **Log Isolation:** Loggers must be named specifically to the application (e.g., `nibandha.amsha`) and stored in `.Nibandha/{App_Name}/logs/`.

## ✅ Quality Standards
- **Testing:** Every new module must have a corresponding test file in `tests/unit/` and a scenario entry in `docs/test/`.
- **Documentation:** New features must include a Markdown file in `docs/modules/` and a reference in `docs/modules/README.md`.