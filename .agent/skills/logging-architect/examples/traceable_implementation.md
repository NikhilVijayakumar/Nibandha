To achieve "Deep Traceability," the agent must understand the difference between **Lazy Logging** (which creates "black boxes") and **Architectural Logging** (which maps code directly to the blueprint).

Here is the improved **Traceable Implementation Gold Standard** for your `logging-architect/examples/` folder.

---

### 📂 `examples/traceable_implementation.md`

# Deep Traceability: Do's and Don'ts

The goal of logging in Nibandha is to allow a developer to look at a production log and immediately identify which **Blueprint ID** failed without opening the source code.

---

## ❌ The "Don't": Lazy & Untraceable Implementation

*This code is hard to debug because it lacks context, uses forbidden `print()`, and has no mapping to the blueprint.*

```python
# UNTRACEABLE VERSION
import os

class FileShifter:
    def move(self, source, dest):
        print(f"Moving {source} to {dest}") # ❌ FORBIDDEN: print() used
        try:
            os.rename(source, dest)
            print("Done") # ❌ FORBIDDEN: print() used
        except Exception:
            print("Error happened") # ❌ FORBIDDEN: No error context/stack trace

```

**Why this fails:**

1. **Black Box:** If it fails, we don't know which requirement (ID) it was trying to satisfy.
2. **Library Pollution:** The `print()` statement forces output to the user's console, which the user cannot turn off or redirect to a file.
3. **Missing Context:** "Error happened" doesn't tell us *what* error (Permission? Disk Full?).

---

## ✅ The "Do": Deeply Traceable Implementation

*This code follows the **3-Stage TDD workflow**. It uses the Protocol, logs Blueprint IDs, and provides execution context.*

```python
from nibandha.domain.protocols import LoggerProtocol
import logging
import os

class FileShifter:
    def __init__(self, logger: LoggerProtocol):
        # ✅ Standard: Contextual logger name
        self.logger = logger 

    def move_log_file(self, source: str, dest: str):
        # ✅ Requirement Mapping: Links directly to Blueprint ID AR-UT-005
        self.logger.info("[AR-UT-005] Initiating atomic file shift: %s -> %s", source, dest)
        
        try:
            if not os.path.exists(source):
                # ✅ Specificity: Log the reason for logic-branching
                self.logger.warning("[AR-UT-005] Shift aborted: Source file missing.")
                return

            os.rename(source, dest)
            self.logger.debug("[AR-UT-005] Shift completed successfully.")
            
        except OSError as e:
            # ✅ Debugging: Log the actual OS error with the Blueprint ID
            self.logger.error("[AR-UT-005] Critical failure during file shift: %s", str(e))
            raise e

```

**Why this succeeds:**

1. **ID Alignment:** If a customer reports an error log containing `[AR-UT-005]`, the developer instantly opens `docs/test/archiver/unit_test_scenarios.md` to see exactly what that logic was supposed to do.
2. **Zero-Print:** The user can configure the log level (INFO vs DEBUG) to keep their console clean.
3. **No Side-Effects:** The logger is passed in (Dependency Injection), ensuring the module doesn't create unwanted files on its own.

---

### 💡 Summary of "Deep Traceability" Rules

| Feature | Rule |
| --- | --- |
| **Logic Gate** | Every `if/else` or `try/except` must have a log entry. |
| **Identifier** | Every `logger.info/error` must start with the `[XX-UT-00X]` ID. |
| **Naming** | Logger names must include the class name for easy filtering. |
| **Error Handling** | Always log the exception message, not just "An error occurred." |
