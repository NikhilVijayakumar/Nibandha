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
    from nibandha import Nibandha
    from nibandha.configuration.domain.models.app_config import AppConfig
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

def main():
    print(">>> Nibandha System Verification (Full Config) <<<")

    # 1. Load Config
    config_path = Path(__file__).parent / "config" / "demo_config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        app_config = AppConfig(**yaml.safe_load(f).get('app', {}))

    print(f"✅ App Config Loaded: {app_config.name}")
    
    # Verify Logging Config
    if app_config.logging:
        print(f"   [Logging] Enabled: {app_config.logging.enabled}")
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
    # Should use the logging config from AppConfig
    app = Nibandha(app_config).bind()
    print(f"✅ Bound to: {app.app_root}")
    
    # Verify app actually used the logging config
    if app.rotation_config and app.rotation_config.backup_count == 3:
         print(f"   ✅ App applied logging config correctly (Backup Count: 3)")
    else:
         print(f"   ❌ App failed to apply logging config. Current: {app.rotation_config}")

    # 3. Generate Reports (Zero Args)
    print("\n[3] Generating Reports...")
    # Generate report using correct config
    # Note: verification might fail since 'docs/specs/functional' doesn't exist, but generation logic should run.
    # We expect missing artifacts because the doc paths are fake, but the *configuration* passing is what we test.
    
    # We can handle missing docs gracefully, verification just checks report existence.
    try:
        success, missing = app.generate_report()
        if success:
            print("✅ Reports Generated & Verified Successfully!")
        else:
            print(f"❌ Verification Failed (Expected if docs missing). Missing: {missing}")
            
    except Exception as e:
        print(f"❌ Generation crashed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
