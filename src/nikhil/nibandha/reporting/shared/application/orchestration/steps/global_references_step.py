import logging
from ..steps_protocol import ReportingStep
from ..context import ReportingContext
from nibandha.reporting.shared.constants import REPORT_FILENAME_REFERENCES

logger = logging.getLogger("nibandha.reporting.steps.references")

class GlobalReferencesStep(ReportingStep):
    def execute(self, context: ReportingContext) -> None:
        logger.info("Generating global references document")
        references = context.reference_collector.get_all_references()
        data = {
            "date": context.timestamp,
            "figures": [fig.model_dump() for fig in references.figures],
            "tables": [tab.model_dump() for tab in references.tables],
            "nomenclature": [nom.model_dump() for nom in references.nomenclature],
            "project_name": context.project_name
        }
        output_path = context.output_dir / "details" / REPORT_FILENAME_REFERENCES
        output_path.parent.mkdir(parents=True, exist_ok=True)
        context.template_engine.render("global_references_template.md", data, output_path)
