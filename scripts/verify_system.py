import sys
import logging
from pathlib import Path
import yaml
import shutil

# Add src to path to ensure we use the local package
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

NIBANDHA_INSTALLED = False
try:
    from nibandha import Nibandha
    from nibandha.configuration.infrastructure.file_loader import FileConfigLoader
    from nibandha.configuration.domain.models.app_config import AppConfig
    from nibandha.configuration.domain.models.reporting_config import ReportingConfig
    from nibandha.reporting import ReportGenerator
    from nibandha.reporting.shared.data.data_builders import SummaryDataBuilder
    NIBANDHA_INSTALLED = True
except ImportError:
    NIBANDHA_INSTALLED = False

def run_basic_verification():
    """Fallback when Nibandha is not installed."""
    print("\n[⚠️] Nibandha Module NOT found. Running Basic Verification (Pytest only).")
    import subprocess
    import json
    
    # 1. Run Unit Tests with JSON output
    # We use a fixed path that the agent expects: .Nibandha/VerificationApp/Report/assets/data/unit.json
    # Or just a temporary path and print it.
    output_dir = Path(".agent_reports/assets/data")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    unit_json = output_dir / "unit.json"
    
    cmd = [sys.executable, "-m", "pytest", "tests/unit", f"--json-report-file={unit_json}", "--json-report"]
    print(f"    Running: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=False) # Don't error if tests fail, we want the report
        if unit_json.exists():
            print(f"    ✅ Unit Test Report generated: {unit_json}")
            
            # Read to verify basic pass/fail
            with open(unit_json) as f:
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
        # Use the app's Report folder to follow unified root design
        report_dir = app.app_root / "Report"
        generator = ReportGenerator(output_dir=str(report_dir))
        print(f"    Generator Output Dir: {generator.output_dir}")
        
        # Define targets - using the script's own dir as a 'package' target to avoid long scans
        # and using a specific test dir for unit/e2e if they exist, else just dummy paths
        # verifying failure handling is also important.
        
        # Custom execution instead of generate_all to capture data
        timestamp = "2023-01-01" # Mock or real, doesn't matter for this capture
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. Unit
        unit_data = generator.run_unit_Tests("tests/unit", timestamp)
        
        # 2. E2E
        e2e_data = generator.run_e2e_Tests("tests/e2e", timestamp)

        # 3. Quality
        quality_data = generator.run_quality_checks("src/nikhil/nibandha")
        
        # 4. Dependencies
        actual_src_root = Path(__file__).parent.parent / "src/nikhil/nibandha"
        dep_data = generator.run_dependency_checks(
            actual_src_root,
            package_roots=["nikhil.nibandha"]
        )
        
        # 5. Packages
        project_root = generator.output_dir.parent.parent
        pkg_data = generator.run_package_checks(project_root)

        # 6. Documentation (use actual project root, not .Nibandha)
        actual_project_root = Path(__file__).parent.parent  # /scripts/../ = project root
        doc_data = generator.run_documentation_checks(actual_project_root)



        # Save Quality JSON for Agent Consumption
        quality_json_path = generator.output_dir / "assets" / "data" / "quality.json"
        quality_json_path.parent.mkdir(parents=True, exist_ok=True)
        import json
        with open(quality_json_path, 'w') as f:
            json.dump(quality_data, f, indent=2, default=str)
        print(f"    ✅ Quality Artifact saved: {quality_json_path}")

        # Save Dependency JSON
        dep_json_path = generator.output_dir / "assets" / "data" / "dependency.json"
        with open(dep_json_path, 'w') as f:
            json.dump(dep_data, f, indent=2, default=str)
        print(f"    ✅ Dependency Artifact saved: {dep_json_path}")

        # Save Package JSON
        pkg_json_path = generator.output_dir / "assets" / "data" / "package.json"
        with open(pkg_json_path, 'w') as f:
            json.dump(pkg_data, f, indent=2, default=str)
        print(f"    ✅ Package Artifact saved: {pkg_json_path}")

        # Save Documentation JSON (Ensuring it is saved even if generator doesn't)
        doc_json_path = generator.output_dir / "assets" / "data" / "documentation.json"
        with open(doc_json_path, 'w') as f:
            json.dump(doc_data, f, indent=2, default=str)
        print(f"    ✅ Documentation Artifact saved: {doc_json_path}")

        # Generate Unified Summary
        summary_builder = SummaryDataBuilder()
        summary_data = summary_builder.build(unit_data, e2e_data, quality_data, documentation_data=doc_data, dependency_data=dep_data, package_data=pkg_data)
        generator.template_engine.render(
            "unified_overview_template.md",
            summary_data,
            generator.output_dir / "summary.md"
        )
        print(f"    ✅ Summary Report generated: {generator.output_dir / 'summary.md'}")

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
