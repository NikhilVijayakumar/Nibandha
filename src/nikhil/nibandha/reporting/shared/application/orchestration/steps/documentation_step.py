import logging
import json
from pathlib import Path
from ..steps_protocol import ReportingStep
from ..context import ReportingContext

logger = logging.getLogger("nibandha.reporting.steps.documentation")

class DocumentationStep(ReportingStep):
    def __init__(self, reporter, project_root: Path):
        self.reporter = reporter
        self.project_root = project_root

    def execute(self, context: ReportingContext) -> None:
        try:
             doc_data = self.reporter.generate(self.project_root, project_name=context.project_name)
             
             json_path = context.output_dir / "assets" / "data" / "documentation.json"
             json_path.parent.mkdir(parents=True, exist_ok=True)

             with open(json_path, 'w', encoding='utf-8') as f:
                 json.dump(doc_data, f, indent=2, default=str)
                 
             context.data["documentation_data"] = doc_data
        except Exception as e:
             logger.warning(f"Documentation check failed: {e}")
             context.data["documentation_data"] = None
