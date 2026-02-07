import logging
from pathlib import Path
from typing import Optional, List
from ..steps_protocol import ReportingStep
from ..context import ReportingContext

logger = logging.getLogger("nibandha.reporting.steps.dependency")

class DependencyCheckStep(ReportingStep):
    def __init__(self, reporter, source_root: Path, package_roots: Optional[List[str]] = None):
        self.reporter = reporter
        self.source_root = source_root
        self.package_roots = package_roots

    def execute(self, context: ReportingContext) -> None:
        logger.info(f"Running dependency checks on source: {self.source_root}")
        result_data = self.reporter.generate(self.source_root, self.package_roots, project_name=context.project_name)
        context.data["dependency_data"] = result_data
