import sys
import yaml
from pathlib import Path
import matplotlib

# Force Matplotlib backend to Agg
matplotlib.use('Agg')

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from nibandha.core.nibandha_app import Nibandha
    from nibandha.configuration.domain.models.app_config import AppConfig
    from nibandha.configuration.application.configuration_manager import ConfigurationManager
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

def main():
    print(">>> Nibandha System Verification (Full Config) <<<")

    # 1. Load Config
    config_path = Path(__file__).parent / "config" / "demo_config.yaml"
    
    # Use ConfigurationManager
    try:
        app_config = ConfigurationManager.load_from_yaml(config_path)
    except Exception as e:
        print(f"❌ Configuration Load Error: {e}")
        sys.exit(1)

    print(f"✅ App Config Loaded: {app_config.name}")
    
    # Verify Logging Config
    if app_config.logging:
        print(f"   [Logging] Level: {app_config.logging.level}")
        print(f"   [Logging] Rotation Enabled: {app_config.logging.rotation_enabled}")
        print(f"   [Logging] Retention: {app_config.logging.archive_retention_days} days")
    else:
        print("   ❌ Logging config missing!")

    # Verify Reporting Config & Doc Paths
    if app_config.reporting:
        print(f"   [Reporting] Quality Target: {app_config.reporting.quality_target}")
        print(f"   [Reporting] Doc Paths: {app_config.reporting.doc_paths}")
    else:
        print("   ❌ Reporting config missing!")

    # 2. Initialize & Bind
    # Using Builder Method
    app = Nibandha.from_config(app_config).bind()
    print(f"✅ Bound to: {app.app_root}")
    
    # Verify app actually used the logging config
    # Nibandha.rotation_config accesses internal coordinator's rotation config (LogRotationConfig)
    if app.rotation_config and app.rotation_config.backup_count == 3:
         print(f"   ✅ App applied logging config correctly (Backup Count: 3)")
    else:
         print(f"   ❌ App failed to apply logging config. Current: {app.rotation_config}")

    # 3. Generate Reports
    print("\n[3] Generating Reports...")
    try:
        # Note: We rely on the config to set targets, but we can override if needed.
        # Here we trust the loaded config.
        success, missing = app.generate_report(project_root=str(project_root))
        
        # We expect failure in "success" because doc paths in demo_config don't exist, 
        # but if we get here, the ENGINE is working.
        if success:
            print("✅ Reports Generated & Verified Successfully!")
        else:
            print(f"⚠️  Verification checks failed (Expected for demo paths). Missing/Issues: {len(missing)}")
            
    except Exception as e:
        print(f"❌ Generation crashed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
