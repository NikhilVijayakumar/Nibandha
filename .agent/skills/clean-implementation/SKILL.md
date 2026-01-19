---
name: clean-implementation
description: Translates Kotlin/Java Clean Architecture into Python using Pydantic, strict isolation, and non-interactive config injection.
---
# Clean-Implementation Workflow (Android/Kotlin Standard)

When implementing domain or infrastructure logic, follow these strict architectural standards to ensure library-grade stability.

## 1. Model Translation & Isolation
- **One Class, One File:** Every Pydantic model and implementation class must live in its own file.
- **Naming:** Files use `snake_case.py`; Classes use `PascalCase`.
- **Location:** Models go in `src/nibandha/domain/models/`.
- **No Python Workarounds:** - NO nested functions (functions inside functions).
    - NO nested classes (classes inside functions or other classes).
    - Logic must be flat and accessible for unit testing, adhering to SOLID principles.

## 2. Pydantic Configuration Injection
- **The Contract:** Implementation classes must NEVER parse YAML/JSON/ENV files directly.
- **Injection:** All classes must receive their settings via a **Pydantic Model instance** in the `__init__` constructor.
- **Single Source of Truth:** Whether called by a client (Amsha) or the library's internal loader, the implementation logic only interacts with the Pydantic object.

## 3. Dependency Injection (Constructor-Based)
Mirror the behavior of Dagger/Hilt:
- Use `__init__` for all injections.
- **Type-hinting:** Always inject **Protocols** (from `domain/protocols/`), not concrete implementation classes.
- **Example Pattern:**
```python
class RotationManager:
    def __init__(self, settings: RotationSettings, logger: LoggerProtocol):
        self.settings = settings  # Injected Pydantic Model
        self.logger = logger      # Injected Protocol
```
## 4. Creational Patterns (Library API Design)
To protect the library's integrity and simplify client usage:

- **Client-Facing (Builder):** Complex core classes must provide a `{ClassName}Builder` class.
    - Use private attributes for state management.
    - Implement a **Fluent API** (e.g., `.with_{feature}()` methods that return `self`).
    - The `.build()` method must validate the final state and return the **immutable** instance.
- **Internal (Factory):** Use Factories to instantiate infrastructure components based on the injected Pydantic settings.



## 5. Automation & Non-Interactivity
- **No Hardcoding:** Always use `self.settings.field` instead of hardcoded literals or constants.
- **No Interactive Setup:** Strictly forbid `input()` or CLI prompts. The library must work headlessly via configuration files or environment variables.
- **Fail Fast:** If a required setting is missing and has no default, raise a custom `NibandhaConfigError` immediately.

## 6. Implementation Steps
When building a new feature, the Agent must follow this sequence:
1. **Model:** Define settings in `domain/models/{feature}_settings.py`.
2. **Protocol:** Define the interface in `domain/protocols/{feature}_protocol.py`.
3. **Creational Logic:** Implement the **Builder** (for public API) or **Factory** (for internal components).
4. **Logic:** Implement the class using the injected settings and protocols.
5. **Validation:** Ensure the implementation remains "pure," testable, and environment-agnostic.

## 7. Absolute Import Enforcement
When generating code:
- **Check pyproject.toml:** Determine the base package name.
- **Strict Absolute Imports:** Ensure all `import` and `from ... import` statements use the full path from the package root. 
- **Example:** Even if two files are in the same folder, use `from nikhil.nibandha.domain.models.x import X` instead of `from .x import X`.