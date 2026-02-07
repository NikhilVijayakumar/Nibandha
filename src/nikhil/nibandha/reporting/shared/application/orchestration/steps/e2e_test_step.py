import logging
from ..steps_protocol import ReportingStep
from ..context import ReportingContext
from nibandha.reporting.shared.infrastructure import utils

logger = logging.getLogger("nibandha.reporting.steps.e2e")

class E2ETestStep(ReportingStep):
    def __init__(self, reporter, target: str):
        self.reporter = reporter
        self.target = target

    def execute(self, context: ReportingContext) -> None:
        logger.info(f"Running E2E tests on target: {self.target}")
        context.e2e_target = self.target
        
        json_path = context.output_dir / "assets" / "data" / "e2e.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        
        utils.run_pytest(self.target, json_path)
        data = utils.load_json(json_path)
        
        result_data = self.reporter.generate(data, context.timestamp, project_name=context.project_name) or {}
        context.data["e2e_data"] = result_data
