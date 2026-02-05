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
        with open(config_path, 'r') as f:
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
        
        # 1. Introduction
        generator.intro_reporter.generate()
        print(f"    ✅ Introduction generated")

        # 2. Global References (Generated later, checking logic)
        
        # 3. Unit
        unit_data = generator.run_unit_Tests("tests/unit", timestamp)
        
        # 4. E2E
        e2e_data = generator.run_e2e_Tests("tests/e2e", timestamp)

        # 5,6,7 Quality
        quality_data = generator.run_quality_checks("src/nikhil/nibandha")
        
        # 8. Dependencies
        actual_src_root = Path(__file__).parent.parent / "src/nikhil/nibandha"
        dep_data = generator.run_dependency_checks(
            actual_src_root,
            package_roots=["nikhil.nibandha"]
        )
        
        # 9. Packages
        project_root = generator.output_dir.parent.parent
        pkg_data = generator.run_package_checks(project_root)

        # 10. Documentation
        actual_project_root = Path(__file__).parent.parent
        try:
             doc_data = generator.doc_reporter.generate(actual_project_root)
        except Exception as e:
             print(f"    ⚠️ Documentation check failed: {e}")
             doc_data = None

        # Save Artifacts for Agent
        assets_dir = generator.output_dir / "assets" / "data"
        assets_dir.mkdir(parents=True, exist_ok=True)
        import json
        
        for name, data in [("quality", quality_data), ("dependency", dep_data), ("package", pkg_data), ("documentation", doc_data)]:
             if data:
                 with open(assets_dir / f"{name}.json", 'w') as f:
                     json.dump(data, f, indent=2, default=str)
                 print(f"    ✅ {name.capitalize()} Artifact saved")

        # 11. Conclusion (formerly Unified Summary)
        summary_builder = SummaryDataBuilder()
        summary_data = summary_builder.build(unit_data, e2e_data, quality_data, documentation_data=doc_data, dependency_data=dep_data, package_data=pkg_data)
        
        generator.template_engine.render(
            "conclusion_template.md",
            summary_data,
            generator.output_dir / "details" / "14_conclusion.md"
        )
        if not (generator.output_dir / "details" / "14_conclusion.md").exists():
            print("    🔴 Conclusion Report NOT generated")
        else:
            print(f"    ✅ Conclusion Report generated: {generator.output_dir / 'details/14_conclusion.md'}")
        
        # Save summary data
        with open(assets_dir / "summary_data.json", 'w') as f:
             json.dump(summary_data, f, indent=2, default=str)

        # Generate global references
        print(f"    Generating global references...")
        generator._generate_global_references(timestamp)
        print(f"    ✅ Global references generated")

         # Trigger Export
        print(f"    Values: Triggering Export to {generator.export_formats}...")
        # Note: In Verification Script we are manually triggering _export_reports. 
        # _export_reports in Generator now expects 'introduction.md', 'conclusion.md' etc. in 'details' folder.
        # We ensured they are generated there above.
        generator._export_reports()
        print(f"    ✅ Exports triggered.")

        # Verify output files exist
        details_dir = generator.output_dir / "details"
        conclusion_path = details_dir / "14_conclusion.md"
        
        if conclusion_path.exists():
             print(f"    ✅ Conclusion Report verified at: {conclusion_path}")
        else:
             print(f"    ❌ Conclusion Report missing at: {conclusion_path}")
             
        if (details_dir / "01_introduction.md").exists():
             print(f"    ✅ Introduction verified")
             
        if (details_dir / "03_unit_report.md").exists():
             print(f"    ✅ Unit Report generated")
        
        if (details_dir / "12_package_dependency_report.md").exists():
             print(f"    ✅ Package Report generated")

    except Exception as e:
        print(f"    ❌ Reporting check failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n>>> Verification Complete <<<")

if __name__ == "__main__":
    main()
