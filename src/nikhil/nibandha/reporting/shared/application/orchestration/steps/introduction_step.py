import logging
from ..steps_protocol import ReportingStep
from ..context import ReportingContext

logger = logging.getLogger("nibandha.reporting.steps.introduction")

class IntroductionStep(ReportingStep):
    def __init__(self, reporter):
        self.reporter = reporter

    def execute(self, context: ReportingContext) -> None:
        self.reporter.generate(context.project_name, metadata=context.cover_metadata)
