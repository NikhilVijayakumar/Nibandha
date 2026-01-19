import logging
import yaml
import traceback
from pathlib import Path
from typing import Optional, List, Dict, Any

from nibandha.core.configuration.domain.config import AppConfig
from nibandha.core.bootstrap.application.app import Nibandha
from nibandha.core.rotation.domain.config import LogRotationConfig
from nibandha.reporting.shared.application.generator import ReportGenerator

logger = logging.getLogger("nibandha.reporting.verifier")

class VerificationService:
    """
    Automated verification service for Nibandha System.
    Validates Logging initialization and Report Generation.
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.app: Optional[Nibandha] = None
        self.generator: Optional[ReportGenerator] = None

    def run_verification(
        self,
        app_name: str = "VerificationRun",
        log_dir: Optional[str] = None,
        report_dir: Optional[str] = None,
        config_dir: Optional[str] = None,
        template_dir: Optional[str] = None,
        unit_target: str = "tests/unit",
        e2e_target: str = "tests/e2e",
        package_target: str = "src/nikhil/nibandha",
        viz_provider: Optional[Any] = None
    ) -> bool:
        """
        Executes the full verification suite.
        """
        logger.info(f"=== Verification Started for {app_name} ===")
        
        success = True
        try:
            # 1. Logging Setup with Rotation
            self._setup_logging(app_name, log_dir, config_dir, report_dir)
            
            # 2. Reporting Setup
            self._setup_reporting(report_dir, template_dir, viz_provider)
            
            # 3. Execution
            self._generate_reports(unit_target, e2e_target, package_target)
            
            # 4. Artifact Verification
            if not self._verify_artifacts():
                success = False
                
        except Exception as e:
            logger.error(f"Verification Failed with Exception: {e}")
            logger.error(traceback.format_exc())
            success = False
            
        logger.info(f"=== Verification Complete. Overall Status: {'SUCCESS' if success else 'FAIL'} ===")
        return success

    def _setup_logging(self, app_name: str, log_dir: Optional[str], config_dir: Optional[str], report_dir: Optional[str] = None):
        logger.info("1. Initializing Nibandha Logging System...")
        
        # Default config path if not provided
        if not config_dir:
            c_path = self.project_root / ".Nibandha" / app_name / "config"
        else:
            c_path = Path(config_dir)
            
        c_path.mkdir(parents=True, exist_ok=True)
            
        # Write Rotation Config
        # We enforce rotation to verify structure
        rotation_config = LogRotationConfig(
            enabled=True,
            timestamp_format="%Y-%m-%d",
            max_size_mb=5,
            backup_count=5
        )
        with open(c_path / "rotation_config.yaml", "w") as f:
            yaml.dump(rotation_config.model_dump(), f) # Use model_dump for V2 compat
            
        # App Config
        config = AppConfig(
            name=app_name,
            log_level="INFO",
            log_dir=log_dir,
            config_dir=str(c_path),
            report_dir=report_dir
        )
        
        self.app = Nibandha(config)
        self.app.bind()
        
        # Log location
        # This message will go to the file AND console if configured
        logger.info(f"Nibandha initialized. Log file: {self.app.current_log_file}")

    def _setup_reporting(self, report_dir: Optional[str], template_dir: Optional[str], viz_provider):
        logger.info("2. Initializing Report Generator...")
        
        # Determine output dir
        # If report_dir passed to run_verification is None, we check app.report_dir (from AppConfig)
        # But ReportGenerator needs explicit output_dir if defaulting.
        # nb.report_dir defaults to .Nibandha/App/Report.
        
        out_dir = str(self.app.report_dir) if self.app else report_dir
        
        self.generator = ReportGenerator(
            output_dir=out_dir,
            template_dir=template_dir,
            visualization_provider=viz_provider
        )
        logger.info(f"Report Output Directory: {self.generator.output_dir}")

    def _generate_reports(self, unit, e2e, pkg):
        logger.info("3. Generating Reports...")
        self.generator.generate_all(
            unit_target=unit,
            e2e_target=e2e,
            package_target=pkg,
            project_root=str(self.project_root)
        )
        logger.info("Generation routine completed.")

    def _verify_artifacts(self) -> bool:
        logger.info("4. Verifying Artifacts...")
        base = self.generator.output_dir
        
        expected = [
            "summary.md",
            "details/unit_report.md",
            "details/e2e_report.md",
            "details/architecture_report.md",
            "details/type_safety_report.md",
            "details/complexity_report.md",
            "details/module_dependency_report.md",
            "details/package_dependency_report.md",
            "assets/images/unit_outcomes.png",
            "assets/data/unit.json"
        ]
        
        logger.info(f"Verifying artifacts in: {base}")
        
        missing = []
        for item in expected:
            p = base / item
            if p.exists():
                logger.debug(f"[PASS] Found {item}")
            else:
                logger.error(f"[FAIL] Missing {item} at {p}")
                missing.append(item)
                
        if missing:
            logger.warning(f"Verification found {len(missing)} missing artifacts.")
            return False
            
        logger.info("All expected artifacts found.")
        return True
