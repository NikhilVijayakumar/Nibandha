import logging
from pathlib import Path
from ..steps_protocol import ReportingStep
from ..context import ReportingContext
from nibandha.reporting.shared.infrastructure import utils

logger = logging.getLogger("nibandha.reporting.steps.unit")

class UnitTestStep(ReportingStep):
    def __init__(self, reporter, target: str):
        self.reporter = reporter
        self.target = target

    def execute(self, context: ReportingContext) -> None:
        logger.info(f"Running unit tests on target: {self.target}")
        context.unit_target = self.target # Update context for reference
        
        json_path = context.output_dir / "assets" / "data" / "unit.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Determine Coverage Target
        cov_target = context.quality_target or "src/nikhil/nibandha" 
        # Note: logic copied from generator.py, likely needs cleaner config access
        
        utils.run_pytest(self.target, json_path, cov_target)
        
        data = utils.load_json(json_path)
        cov_data = utils.load_json(Path("coverage.json"))
        
        result_data = self.reporter.generate(data, cov_data, context.timestamp, project_name=context.project_name) or {}
        context.data["unit_data"] = result_data
