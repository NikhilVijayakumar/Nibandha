import logging
from ..steps_protocol import ReportingStep
from ..context import ReportingContext

logger = logging.getLogger("nibandha.reporting.steps.quality")

class QualityCheckStep(ReportingStep):
    def __init__(self, reporter, target_package: str):
        self.reporter = reporter
        self.target_package = target_package

    def execute(self, context: ReportingContext) -> None:
        logger.info(f"Running quality checks on package: {self.target_package}")
        context.quality_target = self.target_package
        
        results = self.reporter.run_checks(self.target_package)
        self.reporter.generate(results, project_name=context.project_name)
        
        context.data["quality_data"] = results
        
        # Extract individual timings
        for key in ["architecture", "type_safety", "complexity", "hygiene", "security", "duplication", "encoding"]:
            if key in results:
                dur = results[key].get("duration", 0.0)
                context.add_timing(f"Quality: {key.replace('_', ' ').title()}", dur)
