# Nibandha Bugs - Summary

This directory documents bugs found in the Nibandha logging library that affect the Amsha integration.

## Critical Bugs

### 1. Handler Attachment Using basicConfig() ⚠️ CRITICAL
**File**: [`handler_attachment_basicConfig.md`](./handler_attachment_basicConfig.md)

**Issue**: Nibandha uses `logging.basicConfig()` which attaches handlers to Python's ROOT logger instead of the application-specific logger (e.g., "Amsha").

**Impact**: 
- ❌ Log files are created but remain EMPTY (0 bytes)
- ✅ Console logs work (StreamHandler on ROOT works)
- ❌ File logs don't work (FileHandler on ROOT not reachable)

**Status**: NOT FIXED - Needs Nibandha library update

**Workaround**: Available in bug documentation

---

### 2. Default Timestamp Format Too Granular ⚠️ MEDIUM  
**File**: [`logger_timestamp_default.md`](./logger_timestamp_default.md)

**Issue**: Default `timestamp_format` is `%Y-%m-%d_%H-%M-%S` (includes time), causing a new log file on every restart.

**Impact**:
- Multiple log files per day
- Log fragmentation
- Harder log analysis

**Status**: 
- ✅ FIXED in Amsha (`logger.py` line 256)
- ❌ NOT FIXED in Nibandha default

---

## How These Bugs Interact

The two bugs compound each other:

1. **Timestamp issue** creates new files on restart with names like `2026-01-15_10-30-15.log`
2. **Handler issue** makes ALL log files empty (0 bytes)
3. **Result**: Multiple empty log files, no actual logging

## Fix Priority

1. **CRITICAL**: Fix `handler_attachment_basicConfig.md` FIRST
   - Without this, no logs are written regardless of timestamp
   - Blocks all other logging functionality

2. **MEDIUM**: Fix `logger_timestamp_default.md` SECOND
   - After handler fix, this ensures proper file consolidation
   - Improves log organization

## Testing After Fixes

Once both bugs are fixed in Nibandha:

```bash
# Run example app
cd E:/Python/Amsha
.\venv\Scripts\python.exe example\crew_forge\example_app.py

# Check logs
Get-ChildItem .Nibandha\Amsha\logs\data

# Expected result:
# - ONE log file: 2026-01-15.log
# - File is NOT empty
# - Contains all application logs

Get-Content .Nibandha\Amsha\logs\data\2026-01-15.log | Select-Object -Last 20
```

## Impact on Amsha

Currently, Amsha has implemented workarounds:
- ✅ Timestamp format fixed in default config
- ❌ Handler attachment workaround not yet implemented (logs still don't write)

Next steps for Amsha:
1. Implement handler attachment workaround in `logger.py`
2. Update to newer Nibandha version once fixes are available
3. Remove workarounds when Nibandha is fixed

## Reporting to Nibandha

These bugs should be reported to the Nibandha maintainers with:
- Bug descriptions from this directory
- Test cases demonstrating the issues
- Proposed fixes with rationale
- Verification steps

## Related Documentation

### Amsha Bug Reports
- `../../../bugs/logger_propagation.md` - Can't be fixed until Nibandha handler issue resolved
- `../../../bugs/logger_timestamp.md` - Timestamp format issue (partially fixed)

### Amsha Implementation
- `../../../src/nikhil/amsha/common/logger.py` - Current logger implementation
- `../client_quickstart.md` - Client documentation for Nibandha usage
- `../log_rotation_guide.md` - Log rotation documentation
