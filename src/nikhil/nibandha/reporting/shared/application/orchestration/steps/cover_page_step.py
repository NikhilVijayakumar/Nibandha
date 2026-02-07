import logging
from ..steps_protocol import ReportingStep
from ..context import ReportingContext

logger = logging.getLogger("nibandha.reporting.steps.cover_page")

class CoverPageStep(ReportingStep):
    def __init__(self, reporter):
        self.reporter = reporter

    def execute(self, context: ReportingContext) -> None:
        context.cover_metadata = self.reporter.generate(context.source_root.parent, context.timestamp)
        if context.cover_metadata.get("project_name"):
            context.project_name = context.cover_metadata["project_name"]
