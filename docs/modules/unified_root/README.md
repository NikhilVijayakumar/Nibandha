# Unified Root (Nibandha Facade)

## Overview
The `nibandha.unified_root` module is the entry point for the library. It is responsible for "binding" the application to the filesystem, creating necessary directories, and initializing the logging system.

It follows **Clean Architecture**, separating the "Physical State" (Context) from the "creation logic" (Binder) and the "user-facing API" (Facade).

## Architecture

### Domain Layer
Located in `src/nikhil/nibandha/unified_root/domain`.

- **`RootContext` (Model)**: An immutable object representing the resolved paths of the workspace (`root`, `app_root`, `config_dir`, etc.).
- **`RootBinderProtocol` (Protocol)**: Interface for creating the directory structure.

### Infrastructure Layer
Located in `src/nikhil/nibandha/unified_root/infrastructure`.

- **`FileSystemBinder`**: The standard implementation that creates real directories on the OS filesystem.

### Application Layer (Facade)
- **`Nibandha`**: The main class users interact with. It orchestrates the Configuration, Binder, and Logging modules.

## Usage

### Basic Initialization

```python
from nibandha import Nibandha, AppConfig

# 1. Define Config
config = AppConfig(name="Amsha")

# 2. Initialize Facade
# (Uses default FileSystemBinder)
app = Nibandha(config)

# 3. Bind (Creates folders & setups logging)
app.bind()

# Access resolved paths
print(f"App Root: {app.app_root}")
print(f"Logs: {app.context.log_base}")
```

### Advanced: Custom Binder (e.g., In-Memory for Testing)

```python
class InMemoryBinder:
    def bind(self, config, root_name):
        # ... logic to create mock paths ...
        return RootContext(...)

app = Nibandha(config, binder=InMemoryBinder())
app.bind()
```

## Setup Sequence
When `app.bind()` is called:
1.  **Rotation Config Loading**: Checks for `rotation_config.yaml` or uses defaults.
2.  **Binding**: The `Binder` calculates paths and creates directories (Config, Reports, Logs).
3.  **Logging Setup**: Initializes the `NibandhaLogger`.
4.  **Rotation**: If enabled, performs startup archiving/cleanup.
