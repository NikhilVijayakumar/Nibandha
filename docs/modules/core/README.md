# Core Module

## Overview
The Core module is the heart of the Nibandha library, responsible for initialization, configuration management, and establishing the unified root directory structure.

## Components

### 1. Initialization
The `Nibandha` class is the main entry point. It orchestrates the setup of the application environment.
- **Reference**: `src/nikhil/nibandha/core.py` (Nibandha class)

### 2. Configuration
Nibandha uses `AppConfig` to manage application settings such as the application name, log level, and custom folder structures.
- **Detailed Documentation**: [Configuration](configuration.md)

### 3. Unified Root
Nibandha enforces a strict directory structure under `.Nibandha/` to ensure consistency across all applications (Pravaha, Akashavani, Amsha).
- **Detailed Documentation**: [Unified Root](unified-root.md)

## Usage
```python
from nibandha.core import Nibandha, AppConfig

config = AppConfig(name="MyApp", log_level="DEBUG")
app = Nibandha(config)
bound_app = app.bind()
```
