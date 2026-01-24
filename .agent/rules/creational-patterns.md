# Creational Design Rules

## 1. Client-Facing: The Builder Pattern
- **Rule:** Clients (like Amsha/Pravaha) should never call `__init__` on complex core classes.
- **Requirement:** Provide a `Builder` class for the main entry points (e.g., `NibandhaBuilder`).
- **Standard:** Use a fluent interface (e.g., `.with_config().with_logger().build()`).

## 2. Internal-Only: The Factory Pattern
- **Rule:** Use Factories for creating infrastructure objects (e.g., `LoggerFactory`, `StorageFactory`).
- **Logic:** Factories should handle the "selection" logic (e.g., choosing between `RotatingFileHandler` or `StreamHandler`) based on the injected Pydantic Settings.

## 3. Implementation Constraint
- Mark `__init__` methods as "Internal" using documentation or Type Hints if they are intended to be called only by Factories.