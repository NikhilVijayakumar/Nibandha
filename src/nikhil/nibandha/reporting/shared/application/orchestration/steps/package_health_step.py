import logging
from pathlib import Path
from ..steps_protocol import ReportingStep
from ..context import ReportingContext

logger = logging.getLogger("nibandha.reporting.steps.package")

class PackageHealthStep(ReportingStep):
    def __init__(self, reporter, project_root: Path):
        self.reporter = reporter
        self.project_root = project_root

    def execute(self, context: ReportingContext) -> None:
        logger.info(f"Running package checks on project: {self.project_root}")
        result_data = self.reporter.generate(self.project_root, project_name=context.project_name)
        context.data["package_data"] = result_data
