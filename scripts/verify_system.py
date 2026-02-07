import sys
import logging
from pathlib import Path
import yaml
import shutil
import datetime

# Add src to path to ensure we use the local package
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Force Matplotlib backend to Agg to prevent freezing on Windows
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Enforce UTF-8 for Windows Console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

NIBANDHA_INSTALLED = False
try:
    from nibandha import Nibandha
    from nibandha.configuration.infrastructure.file_loader import FileConfigLoader
    from nibandha.configuration.domain.models.app_config import AppConfig
    from nibandha.configuration.domain.models.reporting_config import ReportingConfig
    from nibandha.reporting import ReportGenerator
    from nibandha.reporting.shared.data.data_builders import SummaryDataBuilder
    NIBANDHA_INSTALLED = True
    
    # Resolve Pydantic Forward Refs
    try:
        from nibandha.reporting.shared.domain.protocols.module_discovery import ModuleDiscoveryProtocol
        ReportingConfig.model_rebuild()
    except ImportError as e:
        print(f"Warning: Could not rebuild ReportingConfig: {e}")
except ImportError:
    NIBANDHA_INSTALLED = False

def run_basic_verification():
    """Fallback when Nibandha is not installed."""
    print("\n[⚠️] Nibandha Module NOT found. Running Basic Verification (Pytest only).")
    import subprocess
    import json
    
    output_dir = Path(".agent_reports/assets/data")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    unit_json = output_dir / "unit.json"
    
    cmd = [sys.executable, "-m", "pytest", "tests/unit", f"--json-report-file={unit_json}", "--json-report"]
    print(f"    Running: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=False) 
        if unit_json.exists():
            print(f"    ✅ Unit Test Report generated: {unit_json}")
            with open(unit_json, encoding='utf-8') as f:
                data = json.load(f)
                summary = data.get("summary", {})
                passed = summary.get("passed", 0)
                failed = summary.get("failed", 0)
                print(f"       Passed: {passed}, Failed: {failed}")
        else:
            print("    ❌ Failed to generate JSON report. Install pytest-json-report.")
            
    except Exception as e:
        print(f"    ❌ Execution failed: {e}")
        
    print("\n[ℹ️] Note: Advanced reports (Architecture, Complexity, Dependencies) require 'nibandha' module.")

def main():
    print(">>> Nibandha System Verification <<<")
    
    if not NIBANDHA_INSTALLED:
        run_basic_verification()
        return

    # 1. Load Configuration from YAML
    config_path = Path(__file__).parent / "config" / "demo_config.yaml"
    print(f"\n[1] Loading Configuration from: {config_path}")
    
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        sys.exit(1)
        
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            raw_config = yaml.safe_load(f)
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
        report_dir = app.app_root / "Report"
        
        config = ReportingConfig(
            output_dir=str(report_dir),
            docs_dir=str(app.app_root.parent / "docs"),
            export_formats=["md", "html", "docx"],
            project_name="VerificationApp",
            quality_target="src/nikhil/nibandha",
            package_roots=["nikhil", "nibandha"]
        )
        
        generator = ReportGenerator(config=config)
        print(f"    Generator Output Dir: {generator.output_dir}")
        print(f"    Export Formats: {generator.export_formats}")
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        

        # 3. Unit, E2E, Quality, Dependency, Package, Documentation, Conclusion -> ALL in generate_all
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print("    Running unified report generation...")
        generator.generate_all(
            unit_target="tests/unit",
            e2e_target="tests/e2e/reporting",
            quality_target="src/nikhil/nibandha",
            project_root=str(app.app_root.parent)
        )
        
        # Verify output files exist
        details_dir = generator.output_dir / "details"
        
        checks = [
            "00_cover_page.md",
            "01_introduction.md",
            "03_unit_report.md",
            "04_e2e_report.md",
            "12_package_dependency_report.md",
            "14_encoding_report.md",
            "15_conclusion.md"
        ]
        
        for check in checks:
            path = details_dir / check
            if path.exists():
                print(f"    ✅ Verified: {check}")
            else:
                print(f"    ❌ Missing: {check}")
                
        # Exports are triggered within generate_all if configured
        print(f"    ✅ Verification run complete.")

    except Exception as e:
        print(f"    ❌ Reporting check failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n>>> Verification Complete <<<")

if __name__ == "__main__":
    main()
