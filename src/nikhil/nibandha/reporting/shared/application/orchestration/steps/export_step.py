import logging
from ..steps_protocol import ReportingStep
from ..context import ReportingContext
from nibandha.reporting.shared.constants import (
    REPORT_FILENAME_CONCLUSION, REPORT_FILENAME_REFERENCES,
    REPORT_FILENAME_COVER, REPORT_FILENAME_INTRO, REPORT_FILENAME_UNIT,
    REPORT_FILENAME_E2E, REPORT_FILENAME_ARCHITECTURE, REPORT_FILENAME_TYPE_SAFETY,
    REPORT_FILENAME_COMPLEXITY, REPORT_FILENAME_HYGIENE, REPORT_FILENAME_DUPLICATION,
    REPORT_FILENAME_SECURITY, REPORT_FILENAME_DEPENDENCY_MODULE,
    REPORT_FILENAME_DEPENDENCY_PACKAGE, REPORT_FILENAME_DOCUMENTATION, 
    REPORT_FILENAME_ENCODING
)

logger = logging.getLogger("nibandha.reporting.steps.export")

class ExportStep(ReportingStep):
    def execute(self, context: ReportingContext) -> None:
        # Generate Performance Charts with FULL timings
        full_perf_timings = [{"stage": k, "duration": f"{v:.2f}s"} for k, v in context.timings.items()]
        context.viz_provider.generate_performance_charts(full_perf_timings, context.output_dir / "assets" / "images")

        if not context.export_service:
            return
            
        # Get formats from context
        formats = [f for f in context.export_formats if f != "md"]
        
        if not formats:
            return

        logger.info(f"Exporting reports to: {formats}")
        
        details_dir = context.output_dir / "details"
        
        ordered_files = [
            REPORT_FILENAME_COVER, REPORT_FILENAME_INTRO, REPORT_FILENAME_REFERENCES,
            REPORT_FILENAME_UNIT, REPORT_FILENAME_E2E, REPORT_FILENAME_ARCHITECTURE,
            REPORT_FILENAME_TYPE_SAFETY, REPORT_FILENAME_COMPLEXITY, REPORT_FILENAME_HYGIENE,
            REPORT_FILENAME_DUPLICATION, REPORT_FILENAME_SECURITY, REPORT_FILENAME_DEPENDENCY_MODULE,
            REPORT_FILENAME_DEPENDENCY_PACKAGE, REPORT_FILENAME_DOCUMENTATION, 
            REPORT_FILENAME_ENCODING, REPORT_FILENAME_CONCLUSION
        ]
        
        detail_paths = []
        if details_dir.exists():
            for name in ordered_files:
                path = details_dir / name
                if path.exists():
                    detail_paths.append(path)
        
        # Project Info
        project_info = {"name": context.project_name, "grade": "N/A", "status": "Complete"}
        if "summary_data" in context.data:
            sd = context.data["summary_data"]
            project_info = {
                "name": context.project_name, 
                "grade": sd.get("display_grade", "F"), 
                "status": sd.get("overall_status", "Unknown")
            }
            
        dummy_summary = context.output_dir / "non_existent_summary.md"
        
        if detail_paths:
            context.export_service.export_unified_report(
                dummy_summary,
                detail_paths,
                context.output_dir,
                formats,
                project_info
            )
