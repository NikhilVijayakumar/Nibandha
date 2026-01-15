# Nibandha Bug: Default Timestamp Format Too Granular

## Priority
**MEDIUM** - Causes file proliferation

## Issue
The default `timestamp_format` in Nibandha's `LogRotationConfig` is `%Y-%m-%d_%H-%M-%S`, which includes hours, minutes, and seconds. This causes a NEW log file to be created on every application restart instead of appending to the same daily log file.

## Impact
- **File Proliferation**: Multiple log files per day (one per restart)
- **Log Fragmentation**: Logs scattered across files instead of consolidated
- **Storage Waste**: Unnecessary file creation
- **Harder Log Analysis**: Need to check multiple files for same-day activity

## Root Cause

### Location
`nibandha/core.py` line 27

### Current Code
```python
class LogRotationConfig(BaseModel):
    """Configuration for log rotation and archival."""
    enabled: bool = False
    max_size_mb: int = 10
    rotation_interval_hours: int = 24
    archive_retention_days: int = 30
    log_data_dir: str = "logs/data"
    archive_dir: str = "logs/archive"
    timestamp_format: str = "%Y-%m-%d_%H-%M-%S"  # ❌ Too granular!
```

### Why This Fails

When `_init_logger()` creates the log file (line 125-126):

```python
timestamp = datetime.now().strftime(self.rotation_config.timestamp_format)
log_file = self.app_root / self.rotation_config.log_data_dir / f"{timestamp}.log"
```

With format `%Y-%m-%d_%H-%M-%S`:
- First run at 10:30:15 → `2026-01-15_10-30-15.log`
- Restart at 10:35:42 → `2026-01-15_10-35-42.log` (NEW file!)
- Restart at 14:20:01 → `2026-01-15_14-20-01.log` (ANOTHER new file!)

**Expected Behavior**: All same-day logs should go to `2026-01-15.log`

## Recommended Fix

### Change Default to Daily Granularity

```python
class LogRotationConfig(BaseModel):
    """Configuration for log rotation and archival."""
    enabled: bool = False
    max_size_mb: int = 10
    rotation_interval_hours: int = 24
    archive_retention_days: int = 30
    log_data_dir: str = "logs/data"
    archive_dir: str = "logs/archive"
    timestamp_format: str = "%Y-%m-%d"  # ✅ Daily rotation
```

### Benefits

1. ✅ Same-day restarts append to same log file
2. ✅ New file created only when:
   - Date changes (midnight rollover)
   - Size limit exceeded (`max_size_mb`)
3. ✅ Better log consolidation
4. ✅ Easier log analysis (one file per day)

### Considerations

The timestamp format should match the `rotation_interval_hours` setting:
- `24 hours` → `%Y-%m-%d` (daily)
- `168 hours` (weekly) → `%Y-W%W` (week number)
- `720 hours` (monthly) → `%Y-%m` (monthly)

For sub-daily rotation, keep time component but users should explicitly configure it.

## Impact on Existing Deployments

**Breaking Change**: Yes, for new installations. Existing deployments with cached `rotation_config.yaml` are not affected until they delete and regenerate config.

**Migration Path**:
1. Users with existing configs keep their settings
2. New installations get the improved default
3. Update docs to recommend daily format for 24-hour rotation

## Verification

After fix:

```python
# First run
logger = get_logger()
logger.info("First run")
# Creates: .Nibandha/Amsha/logs/data/2026-01-15.log

# Simulate restart (reset logger)
reset_logger()
logger = get_logger()
logger.info("After restart")
# Appends to: .Nibandha/Amsha/logs/data/2026-01-15.log (SAME file!)
```

## Workaround

Users can manually create/update `.Nibandha/config/rotation_config.yaml`:

```yaml
enabled: true
max_size_mb: 50
rotation_interval_hours: 24
archive_retention_days: 30
log_data_dir: logs/data
archive_dir: logs/archive
timestamp_format: '%Y-%m-%d'  # Daily format
```

Or use Amsha's rotation setup utility:

```python
from amsha.common.rotation_setup import setup_rotation

setup_rotation(
    enabled=True,
    max_size_mb=50,
    rotation_interval=24,
    retention_days=30,
    timestamp_format='%Y-%m-%d'  # Override default
)
```

## Related Issues

- See `handler_attachment_basicConfig.md` - primary handler attachment bug
- This was reported in `../../../bugs/logger_timestamp.md`

## Status

**Fixed in Amsha**: `amsha/common/logger.py` line 256 now uses `%Y-%m-%d` for default config
**Not Fixed in Nibandha**: Still uses `%Y-%m-%d_%H-%M-%S` as default
