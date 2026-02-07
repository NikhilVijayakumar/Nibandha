
import logging
import time
import shutil
from pathlib import Path
from nibandha.core import Nibandha, AppConfig, LogRotationConfig

def test_archival_repro():
    root = Path("temp_repro_root_archival")
    if root.exists():
        shutil.rmtree(root)
    root.mkdir()

    # 1. Config with rotation enabled, ultra-small size limit (0.0001 MB ~ 100 bytes)
    app_config = AppConfig(
        name="ReproApp",
        config_dir=str(root / "config"),
        log_dir=str(root / "logs")
    )

    nb = Nibandha(app_config, root_name=str(root / ".Nibandha"))
    
    # Manually save rotation config to enable it
    nb.config_dir.mkdir(parents=True, exist_ok=True)
    rot_config = LogRotationConfig(
        enabled=True,
        max_size_mb=0.00001, # Extremely small to trigger rotation immediately
        log_data_dir="data",
        archive_dir="archive"
    )
    # Write config manually because bind() reads it
    import yaml
    with open(nb.config_dir / "rotation_config.yaml", 'w') as f:
        yaml.dump(rot_config.dict(), f)

    print("Binding Nibandha...")
    nb.bind()
    print(f"Current log file: {nb.current_log_file}")

    # 2. Generate logs
    logger = logging.getLogger("ReproApp")
    print("Writing logs...")
    for i in range(100):
        logger.info(f"Log line {i} " * 10) # ~100 bytes per line

    # 3. Check if rotation is needed
    should = nb.should_rotate()
    print(f"Should rotate? {should}")
    
    if should:
        print("Rotating logs...")
        nb.rotate_logs()
        
        # 4. Verify Archive
        archive_dir = nb._log_base / "archive"
        archives = list(archive_dir.glob("*"))
        print(f"Archives found: {archives}")
        
        if not archives:
            print("FAILURE: No archives found!")
        else:
            print("SUCCESS: Archive created.")
            
        # Verify new log file exists and is being written to
        print(f"New log file: {nb.current_log_file}")
        logger.info("New log line after rotation")
        
        if nb.current_log_file.exists():
             with open(nb.current_log_file, 'r') as f:
                 content = f.read()
                 if "New log line after rotation" in content:
                     print("SUCCESS: New log file active.")
                 else:
                     print("FAILURE: New log file exists but not written to.")
    else:
        print("FAILURE: Should rotate returned False despite large logs.")

    # Cleanup
    # close handlers to allow delete
    handlers = logger.handlers[:]
    for h in handlers:
        h.close()
        logger.removeHandler(h)
        
    try:
        shutil.rmtree(root)
    except Exception as e:
        print(f"Cleanup warning: {e}")

if __name__ == "__main__":
    test_archival_repro()
