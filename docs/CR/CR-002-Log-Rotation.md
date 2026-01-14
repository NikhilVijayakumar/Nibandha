# CR-002: Log Rotation Support

## Status
- **Date**: 2026-01-13
- **Author**: Amsha Team
- **Priority**: High
- **Status**: ✅ Implemented (2026-01-14)
- **Implementation**: Config-driven rotation with interactive setup, timestamped logs, dual triggers (size/time), auto-archival, and cleanup utilities

## Problem Statement
Currently, Nibandha uses a standard `logging.FileHandler` which appends to a single log file indefinitely. For long-running applications or heavy workloads (like LLM interactions), this file grows unboundedly, eventually consuming all disk space and making log analysis difficult.

## Requirement
The application needs a mechanism to:
1. Limit the size of individual log files.
2. Archive older logs when the size limit is reached.
3. Automatically delete old archives to conserve space.
4. Configure these parameters via `AppConfig`.

## Proposed Solution

### 1. Update `AppConfig`
Introduce a `LogRotationConfig` model and add it to `AppConfig`.

```python
from pydantic import BaseModel
from typing import Optional

class LogRotationConfig(BaseModel):
    enabled: bool = False
    max_bytes: int = 10 * 1024 * 1024  # Default 10 MB
    backup_count: int = 5              # Keep 5 backups

class AppConfig(BaseModel):
    # ... existing fields ...
    rotation: Optional[LogRotationConfig] = None
```

### 2. Update `Nibandha._init_logger`
Use `logging.handlers.RotatingFileHandler` when rotation is enabled.

```python
from logging.handlers import RotatingFileHandler

def _init_logger(self):
    log_file = self.log_dir / f"{self.config.name}.log"
    
    if self.config.rotation and self.config.rotation.enabled:
        handler = RotatingFileHandler(
            log_file,
            maxBytes=self.config.rotation.max_bytes,
            backupCount=self.config.rotation.backup_count
        )
    else:
        handler = logging.FileHandler(log_file)
        
    logging.basicConfig(
        # ... existing config ...
        handlers=[handler, logging.StreamHandler()]
    )
```

## Benefits
- **Disk Safety**: Prevents unbounded log growth.
- **Maintainability**: Smaller, segmented log files are easier to read and grep.
- **Configurable**: Users can tune retention based on their specific needs.
