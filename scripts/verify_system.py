import sys
import logging
from pathlib import Path
import yaml
import shutil

# Add src to path to ensure we use the local package
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from nibandha import Nibandha
from nibandha.configuration.infrastructure.file_loader import FileConfigLoader
from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.configuration.domain.models.reporting_config import ReportingConfig
from nibandha.reporting import ReportGenerator

def main():
    print(">>> Nibandha System Verification <<<")
    
    # 1. Load Configuration from YAML
    config_path = Path(__file__).parent / "config" / "demo_config.yaml"
    print(f"\n[1] Loading Configuration from: {config_path}")
    
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        sys.exit(1)
        
    try:
        # Load Raw Dict
        with open(config_path, 'r') as f:
            raw_config = yaml.safe_load(f)
            
        # Parse App Config
        app_config_data = raw_config.get('app', {})
        app_config = AppConfig(**app_config_data)
        print(f"    ✅ App Config Loaded: {app_config.name} (Level: {app_config.log_level})")
        
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        sys.exit(1)

    # 2. Initialize System
    print(f"\n[2] Initializing Nibandha with Root: Default (.Nibandha)")
    try:
        app = Nibandha(app_config)
        app.bind()
        print(f"    ✅ Bound to: {app.app_root}")
        
    except Exception as e:
        print(f"❌ Failed to initialize app: {e}")
        sys.exit(1)

    # 3. Verify Logging
    print(f"\n[3] Verifying Logging")
    logger = app.logger
    logger.info("Verification: This is an INFO message")
    logger.error("Verification: This is an ERROR message")
    
    # Let's check what file is actually used (this handles rotation/legacy)
    current_log = app.current_log_file
    print(f"    Checking log file: {current_log}")
    
    if current_log and current_log.exists():
        content = current_log.read_text()
        if "Verification: This is an INFO message" in content:
            print(f"    ✅ Log content verified.")
        else:
            print(f"    ❌ Log message missing from file.")
    else:
        print (f"    ❌ Log file not found: {current_log}")

    # 4. Verify Custom Folders
    print(f"\n[4] Verifying Custom Folders")
    for folder in app_config.custom_folders:
        path = app.app_root / folder
        if path.exists():
             print(f"    ✅ Folder exists: {folder}")
        else:
             print(f"    ❌ Folder missing: {folder}")

    # 5. Verify Reporting
    print(f"\n[5] Verifying Reporting")
    try:
        generator = ReportGenerator(config=app_config)
        print(f"    Generator Output Dir: {generator.output_dir}")
        
        # Define targets - using the script's own dir as a 'package' target to avoid long scans
        # and using a specific test dir for unit/e2e if they exist, else just dummy paths
        # verifying failure handling is also important.
        
        print("    Generating full reports...")
        generator.generate_all(
            unit_target="tests/unit",
            e2e_target="tests/e2e",
            package_target="src/nikhil/nibandha" 
        )
        
        # Verify output files exist
        summary_path = generator.output_dir / "summary.md"
        details_dir = generator.output_dir / "details"
        
        if summary_path.exists():
             print(f"    ✅ Summary Report generated: {summary_path}")
        else:
             print(f"    ❌ Summary Report missing")
             
        if (details_dir / "unit_report.md").exists():
             print(f"    ✅ Unit Report generated")
        
        if (details_dir / "package_dependency_report.md").exists():
             print(f"    ✅ Dependency Report generated")

    except Exception as e:
        print(f"    ❌ Reporting check failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n>>> Verification Complete <<<")
    
    # Cleanup (Optional)
    # shutil.rmtree(".Nibandha_Verify", ignore_errors=True)

if __name__ == "__main__":
    main()
