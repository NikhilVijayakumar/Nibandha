from typing import Protocol,runtime_checkable
from .context import ReportingContext

@runtime_checkable
class ReportingStep(Protocol):
    def execute(self, context: ReportingContext) -> None:
        """
        Execute a single reporting step.
        
        Args:
            context: The shared reporting context containing state and services.
        """
        ...
