#!/usr/bin/env python3
"""
Quick verification script to test log archival functionality
Run this to verify the new date-based archival system works correctly
"""

import shutil
from pathlib import Path
from datetime import datetime, timedelta
from nibandha.core import Nibandha, AppConfig, LogRotationConfig

def ping_archival():
    """Quick ping test for log archival system"""
    
    print("=" * 60)
    print("LOG ARCHIVAL SYSTEM - PING TEST")
    print("=" * 60)
    
    # Setup
    root = Path("temp_ping_test")
    if root.exists():
        shutil.rmtree(root)
    
    app_config = AppConfig(
        name="PingTest",
        log_dir=str(root / "logs")
    )
    
    nb = Nibandha(app_config, root_name=str(root / ".Nibandha"))
    
    # Enable rotation with small retention for testing
    nb.config_dir.mkdir(parents=True, exist_ok=True)
    rot_config = LogRotationConfig(
        enabled=True,
        archive_retention_days=5,
        backup_count=2,
        timestamp_format="%Y-%m-%d"
    )
    
    import yaml
    with open(nb.config_dir / "rotation_config.yaml", 'w') as f:
        yaml.dump(rot_config.dict(), f)
    
    print("\n✓ Rotation config created")
    
    # Initialize
    nb.bind()
    print(f"✓ Nibandha initialized at {nb.app_root}")
    
    # Create fake old logs in data/
    data_dir = nb._log_base / "data"
    today = datetime.now().date()
    
    old_dates = [
        ("7 days ago", today - timedelta(days=7)),
        ("5 days ago", today - timedelta(days=5)),
        ("3 days ago", today - timedelta(days=3)),
        ("Yesterday", today - timedelta(days=1)),
    ]
    
    print(f"\n📝 Creating test logs:")
    for label, date in old_dates:
        log_file = data_dir / f"{date.strftime('%Y-%m-%d')}.log"
        log_file.write_text(f"Test log from {label} ({date})\n" * 10)
        print(f"   - {label}: {log_file.name}")
    
    print(f"   - Today: {nb.current_log_file.name} (current)")
    
    # Trigger archival manually
    print("\n🔄 Running archival...")
    archived_count = nb.rotation_manager.archive_old_logs_from_data()
    print(f"✓ Archived {archived_count} old log(s)")
    
    # Show archive structure
    archive_dir = nb._log_base / "archive"
    print(f"\n📦 Archive structure ({archive_dir}):")
    
    if archive_dir.exists():
        for date_folder in sorted(archive_dir.iterdir()):
            if date_folder.is_dir():
                logs = list(date_folder.glob("*.log*"))
                print(f"   {date_folder.name}/")
                for log in logs:
                    size = log.stat().st_size
                    print(f"      └─ {log.name} ({size} bytes)")
    
    # Run cleanup
    print("\n🧹 Running cleanup (retention: 5 days)...")
    cleanup_count = nb.cleanup_old_archives()
    print(f"✓ Cleaned up {cleanup_count} old archive(s)")
    
    # Show final state
    print(f"\n📊 Final state:")
    print(f"   Data folder: {len(list(data_dir.glob('*.log*')))} file(s)")
    
    if archive_dir.exists():
        archive_folders = [f for f in archive_dir.iterdir() if f.is_dir()]
        total_archived = sum(len(list(f.glob('*.log*'))) for f in archive_folders)
        print(f"   Archive: {len(archive_folders)} date folder(s), {total_archived} file(s)")
        print(f"   Folders: {[f.name for f in sorted(archive_folders)]}")
    
    # Cleanup
    print("\n🗑️  Cleaning up test directory...")
    import time
    time.sleep(0.1)  # Let file handles close
    
    # Close logger handlers
    for handler in nb.logger.handlers[:]:
        handler.close()
        nb.logger.removeHandler(handler)
    
    shutil.rmtree(root)
    
    print("\n" + "=" * 60)
    print("✅ PING TEST COMPLETE - Archival system working!")
    print("=" * 60)

if __name__ == "__main__":
    ping_archival()
