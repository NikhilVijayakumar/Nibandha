# DDD & Clean Architecture Structure Rule (Pydantic + Strict Isolation)

## 1. Directory-Based Models
- **Path:** `src/{package}/domain/models/`
- **Rule:** Use "One Class, One File." 
- **Naming:** - Files: `snake_case.py` (e.g., `user_entity.py`)
  - Classes: `PascalCase` (e.g., `UserEntity`)
- **Aggregation:** Use `__init__.py` in the models folder to export classes for easier imports if needed, but the logic remains separate.

## 2. Pydantic & Logic Constraints
- **Inheritance:** All domain models must inherit from `pydantic.BaseModel`.
- **Logic Isolation:** - **No Nested Functions:** Functions must be top-level or class methods.
  - **No Nested Classes:** No classes defined inside functions or other classes.
  - **SOLID Compliance:** Ensure methods are focused. If a model needs complex validation logic, move it to a dedicated `Service` or `Validator` class in the domain layer.

## 3. Mandatory Model Configuration
```python
from pydantic import BaseModel, ConfigDict

class BaseDomainModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,        # Immutable like Kotlin data classes
        strict=True,        # No type coercion
        extra='forbid'      # No extra fields allowed
    )
```