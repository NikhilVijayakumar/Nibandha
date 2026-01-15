# Nibandha Bug: Incorrect Handler Attachment Using basicConfig()

## Priority
**CRITICAL** - Prevents log file writing in all applications

## Issue
Nibandha uses `logging.basicConfig()` to attach file and console handlers, which attaches handlers to Python's ROOT logger instead of the application-specific logger (e.g., "Amsha"). This causes logs to not be written to files when the application logger has `propagate=False` or when multiple loggers are used.

## Impact
- **All log messages appear in console** (StreamHandler on root logger works)
- **NO log messages written to file** (FileHandler on root logger not reached)
- **Affects all applications using Nibandha** for logging

## Root Cause

### Location
`nibandha/core.py` lines 137-145

### Problematic Code
```python
def _init_logger(self):
    """Initialize logging with or without rotation"""
    # ... log file creation ...
    
    # Setup logging
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s'))
    
    logging.basicConfig(              # ❌ PROBLEM: Attaches to ROOT logger
        level=self.config.log_level,
        format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        handlers=[
            handler,
            logging.StreamHandler()
        ]
    )
    self.logger = logging.getLogger(self.config.name)  # Gets "Amsha" logger
    self.logger.info(f"Nibandha initialized at {self.app_root}")
```

### Why This Fails

1. **`logging.basicConfig()` only works ONCE per Python process** - subsequent calls are ignored
2. **It attaches handlers to the ROOT logger** (`logging.root`), not to the named logger
3. **Named loggers need propagate=True to reach ROOT** - but we want `propagate=False` to prevent log leakage
4. **Result**: FileHandler is on ROOT logger, but "Amsha" logger and its children can't reach it

### Handler Hierarchy Problem

```
Python ROOT Logger
├── FileHandler (attached by basicConfig) ✓
├── StreamHandler (attached by basicConfig) ✓
└── (no propagation needed for ROOT)

Amsha Logger (propagate=False to prevent leakage)
├── No handlers directly attached ❌
└── Child loggers (Amsha.crew_forge.application)
    ├── No handlers directly attached ❌
    └── Propagate to parent "Amsha" ✓
        └── Can't reach ROOT handlers ❌ (propagate=False blocks it)
```

## Recommended Fix

### Solution: Attach Handlers Directly to Named Logger

Replace lines 133-145 with:

```python
def _init_logger(self):
    """Initialize logging with or without rotation"""
    if self.rotation_config and self.rotation_config.enabled:
        timestamp = datetime.now().strftime(self.rotation_config.timestamp_format)
        log_file = self.app_root / self.rotation_config.log_data_dir / f\"{timestamp}.log\"
        self.current_log_file = log_file
        self.log_start_time = datetime.now()
    else:
        log_file = self.app_root / \"logs\" / f\"{self.config.name}.log\"
    
    # Get the named logger FIRST
    self.logger = logging.getLogger(self.config.name)
    self.logger.setLevel(self.config.log_level)
    
    # Attach handlers directly to the named logger
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
    )
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
    )
    
    # Add handlers to the NAMED logger, not ROOT
    self.logger.addHandler(file_handler)
    self.logger.addHandler(console_handler)
    
    # Prevent propagation to root logger to avoid duplicate logs
    self.logger.propagate = False
    
    self.logger.info(f\"Nibandha initialized at {self.app_root}\")
    
    if self.rotation_config and self.rotation_config.enabled:
        self.logger.info(f\"Log rotation enabled: {self.current_log_file.name}\")
```

### Benefits of This Fix

1. ✅ Handlers attached directly to "Amsha" logger
2. ✅ Child loggers (Amsha.crew_forge.application) inherit handlers through propagation
3. ✅ No dependency on ROOT logger
4. ✅ Works correctly with `propagate=False` on Amsha logger
5. ✅ File and console logging both work

## Verification

After fix, test:

```python
from nibandha.core import Nibandha, AppConfig

config = AppConfig(name="TestApp")
nib = Nibandha(config).bind()

# Test root logger
nib.logger.info("Test from root logger")

# Test child logger
import logging
child = logging.getLogger("TestApp.module")
child.info("Test from child logger")

# Check .Nibandha/TestApp/logs/data/*.log
# Both messages should appear in the log file
```

## Workaround for Amsha (Until Nibandha Fixed)

In `amsha/common/logger.py`, after Nibandha initialization, manually attach handlers:

```python
_amsha_nibandha = Nibandha(config).bind()

# WORKAROUND: Manually attach handlers to Amsha logger
import logging
amsha_logger = logging.getLogger("Amsha")

# Get handlers from root logger (where basicConfig put them)
root_logger = logging.getLogger()
for handler in root_logger.handlers:
    if isinstance(handler, logging.FileHandler):
        # Attach file handler to Amsha logger
        amsha_logger.addHandler(handler)

# Now we can safely set propagate=False
amsha_logger.propagate = False

_amsha_nibandha.logger.info("Amsha logger initialized via Nibandha")
```

## Related Issues

- See `../../../bugs/logger_propagation.md` - propagation issue can't be fixed until Nibandha handlers are attached correctly
- See `logger_timestamp_default.md` - default timestamp format issue

## Testing

```bash
cd E:/Python/Amsha
.\venv\Scripts\python.exe -c "import sys; sys.path.insert(0, 'src/nikhil'); from amsha.common.logger import get_logger; logger = get_logger('test'); logger.info('Test message'); import time; time.sleep(1)"

# Check log file
Get-Content .Nibandha/Amsha/logs/data/*.log
# Should contain "Test message" - currently it doesn't!
```
