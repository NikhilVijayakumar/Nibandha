---
name: security-and-pitfalls
description: Scans Python code for security vulnerabilities, resource leaks, and library-specific pitfalls.
---
# Security & Pitfalls Workflow

When reviewing or writing code for Nibandha, audit for these specific Python "Gotchas":

## 1. Resource Management (The "Leaky Handle" Problem)
- **Constraint:** All file operations must use the `with` statement (Context Managers) to ensure handles are closed.
- **Logging Rotation:** Ensure that the `RotationManager` does not leave file streams open during the renaming/archiving phase.

## 2. File System Security
- **Path Traversal:** Use `pathlib.Path.resolve()` to validate that the client-provided `root_dir` does not navigate outside the intended workspace (e.g., using `../../`).
- **OS-Agnosticism:** Ensure no forward slashes `/` or backslashes `\` are hardcoded. Use `path / "subdir"` exclusively.

## 3. Subprocess Safety (Reporting Module)
- **Constraint:** When calling `ruff`, `mypy`, or `pytest` via the Reporting module, **never** use `shell=True`.
- **Injection:** Always pass commands as a list (e.g., `["pytest", "--json-report"]`) to prevent shell injection vulnerabilities.

## 4. Default Mutable Arguments
- **Constraint:** Never use a list or dict as a default value in a function signature (e.g., `def task(tags=[])`). Use `None` and initialize inside the function.