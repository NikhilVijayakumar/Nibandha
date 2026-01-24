# Project Config & Initialization Rule

## 1. The Implementation Contract
- **Rule:** Implementation classes (Infrastructure/Domain) must NEVER parse YAML or JSON files directly.
- **Contract:** All classes must receive their configuration as a **Pydantic Model instance** in the `__init__` method.
- **Benefit:** This ensures the logic remains identical whether the library is running in "Standalone Mode" (loading its own YAML) or "Client Mode" (receiving a Pydantic object from a consuming app).

## 2. Configuration Loading (Separation of Concerns)
- **Defaults:** Define sensible defaults within the Pydantic `BaseModel` using `Field(default=...)`.
- **Loading Logic:** Create a dedicated `ConfigLoader` utility in the Infrastructure layer.
  - It handles the hierarchy: `Pydantic Defaults` -> `YAML/JSON File` -> `Environment Variables`.
  - It outputs a validated Pydantic object to be injected into the services.

## 3. Non-Interactive Automation
- **Strictly Prohibited:** `input()` and interactive CLI prompts.
- **Failure Mode:** If a required setting is missing and no default exists, raise a `ConfigurationError`.
- **Environment Agnostic:** Use `pathlib` for any paths resolved during the loading phase.

## 4. One Class, One File
- The Settings model (e.g., `LogSettings`) must live in its own file within `domain/models/`.