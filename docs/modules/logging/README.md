# Module: Logging

## Identity
- **Namespace:** `nikhil.nibandha.logging`
- **Purpose:** Provide a standardized, traceable logging infrastructure for all Nibandha apps.

## Architecture Follows Clean Implementation
The logging module is structured to separate concerns:

- **Domain (`domain/`)**: 
    - **Models:** `LogSettings`, `LogRotationConfig`.
    - **Protocols:** `LoggerProtocol`.
- **Infrastructure (`infrastructure/`)**:
    - **`NibandhaLogger`**: Concrete implementation using Python's `logging` module.
    - **`RotationManager`**: Handles log file rotation and archival.

## Data Structures (Contracts)

### LogSettings
Configuration for *what* to log.
- **Fields:**
    - `app_name` (str): Required.
    - `log_level` (str): default "INFO".

### LogRotationConfig
Configuration for *how* to manage log files.
- **Fields:**
    - `enabled` (bool): Master switch.
    - `log_data_dir`: Directory for active logs.
    - `archive_dir`: Directory for old logs.
    - `rotation_interval_hours`: Frequency.

## Functional Requirements
1.  **Zero-Interaction:** Must not require user input during runtime.
2.  **Structured Format:** `TIMESTAMP | LEVEL | [APP] | Message [IDs]`
3.  **Traceability:** Supports passing `ids` list to track request/task flow.

## Usage

### 1. Basic Usage (via Nibandha Facade)
Most users will not instantiate the logger directly. The `Nibandha` facade handles it.

```python
from nibandha import Nibandha, AppConfig

app = Nibandha(AppConfig(name="MyApp")).bind()
app.logger.info("Application Started", ids=["init-001"])
```

### 2. Manual Usage (Infrastructure)

```python
from nibandha.logging.infrastructure.nibandha_logger import NibandhaLogger

logger = NibandhaLogger("MyApp", "INFO", "/path/to/logfile.log")
logger.info("Manual Log Entry", ids=["manual-task"])
```

## Rotation System
The `RotationManager` handles lifecycle management:
1.  **Startup**: Moves old logs from `log_data_dir` to `archive_dir`.
2.  **Cleanup**: Deletes archives older than `archive_retention_days`.
3.  **Runtime**: Checks `should_rotate()` based on size or time (if implemented).
