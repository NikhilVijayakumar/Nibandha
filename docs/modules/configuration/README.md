# Configuration Module

## Overview
The `nibandha.configuration` module acts as the single source of truth for application configuration. It follows Clean Architecture principles, separating the Domain (Configuration Models & Protocols) from the Infrastructure (Loaders).

## Architecture

### Domain Layer
Located in `src/nikhil/nibandha/configuration/domain`.

- **`AppConfig` (Model)**: A Pydantic model defining the core configuration schema (name, custom folders, log levels, paths).
- **`ConfigLoaderProtocol` (Protocol)**: The interface that any configuration loader must implement.

### Infrastructure Layer
Located in `src/nikhil/nibandha/configuration/infrastructure`.

- **`StandardConfigLoader`**: The default implementation used to build `AppConfig` objects.

## Usage

### 1. Basic Usage (Standard Loader)

```python
from nibandha.configuration.infrastructure.loaders import StandardConfigLoader
from nibandha import Nibandha

# 1. Load Configuration
loader = StandardConfigLoader(
    name="MyApp",
    log_level="DEBUG",
    custom_folders=["data", "output"]
)
config = loader.load()

# 2. Bind Application
app = Nibandha(config).bind()
```

### 2. Environment Variables & File Loading
(Future Extension)
The `ConfigLoaderProtocol` allows for implementing loaders that read from `os.environ` or `.yaml` files seamlessly without changing the core application logic.

## AppConfig Reference

```python
class AppConfig(BaseModel):
    name: str                          # Required: App Name
    custom_folders: List[str] = []     # Optional: Sub-directories to create
    log_level: str = "INFO"            # Optional: Logging Level
    
    # Path Overrides (Optional)
    log_dir: Optional[str] = None
    report_dir: Optional[str] = None
    config_dir: Optional[str] = None
```
