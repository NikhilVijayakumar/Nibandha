from typing import List
import logging
import time
from .context import ReportingContext
from .steps_protocol import ReportingStep

logger = logging.getLogger("nibandha.reporting.orchestrator")

class ReportingOrchestrator:
    def __init__(self, context: ReportingContext, steps: List[ReportingStep]):
        self.context = context
        self.steps = steps
        
    def run(self) -> None:
        """Execute the reporting pipeline."""
        logger.info(f"Starting reporting pipeline for project: {self.context.project_name}")
        
        total_start = time.time()
        
        for step in self.steps:
            step_name = step.__class__.__name__
            logger.debug(f"Executing step: {step_name}")
            try:
                start = time.time()
                step.execute(self.context)
                duration = time.time() - start
                self.context.add_timing(step_name, duration)
                logger.debug(f"Step {step_name} completed in {duration:.2f}s")
            except Exception as e:
                logger.error(f"Error in step {step_name}: {e}", exc_info=True)
                # Decide whether to continue or abort. 
                # For now, we continue as some reports are independent.
                
        total_duration = time.time() - total_start
        logger.info(f"Reporting pipeline completed in {total_duration:.2f}s")
