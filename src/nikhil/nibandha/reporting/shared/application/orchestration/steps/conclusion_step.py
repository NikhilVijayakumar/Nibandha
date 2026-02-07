import logging
import json
from ..steps_protocol import ReportingStep
from ..context import ReportingContext
from nibandha.reporting.shared.constants import REPORT_FILENAME_CONCLUSION
from nibandha.reporting.shared.constants import REPORT_ORDER_CONCLUSION
from nibandha.reporting.shared.application.reference_collector import FigureReference

logger = logging.getLogger("nibandha.reporting.steps.conclusion")

class ConclusionStep(ReportingStep):
    def execute(self, context: ReportingContext) -> None:
        summary_data = context.summary_builder.build(
            context.data.get("unit_data", {}),
            context.data.get("e2e_data", {}),
            context.data.get("quality_data", {}),
            documentation_data=context.data.get("documentation_data"),
            dependency_data=context.data.get("dependency_data"),
            package_data=context.data.get("package_data"),
            timings=context.timings
        )
        
        # [NEW] Generate Conclusion Scorecard Logic (from Generator)
        scorecard_data = {}
        def get_status(grade):
            return "FAIL" if grade in ["F", "-"] else "PASS"

        q_grades = summary_data.get("quality_grades", {})
        for cat, grade in q_grades.items():
            scorecard_data[cat] = {"grade": grade, "status": get_status(grade)}
            
        if "unit_tests" in summary_data:
            u_grade = summary_data["unit_tests"].get("grade", "-")
            scorecard_data["Unit Tests"] = {"grade": u_grade, "status": get_status(u_grade)}
            
        if "e2e_tests" in summary_data:
            e_grade = summary_data["e2e_tests"].get("grade", "-")
            scorecard_data["E2E Tests"] = {"grade": e_grade, "status": get_status(e_grade)}

        conc_charts = context.viz_provider.generate_conclusion_charts(scorecard_data, context.output_dir / "assets" / "images")
        if conc_charts:
            summary_data.update(conc_charts)
            
            # Register Reference
            rel_path = f"assets/images/project_scorecard.png"
            context.reference_collector.add_figure(FigureReference(
                id="fig-project-scorecard",
                title="Project Quality Scorecard",
                path=rel_path,
                type="scorecard",
                description="Summary of project quality grades across all categories",
                source_report="conclusion",
                report_order=REPORT_ORDER_CONCLUSION
            ))

        context.template_engine.render(
             "conclusion_template.md",
             summary_data,
             context.output_dir / "details" / REPORT_FILENAME_CONCLUSION
        )
        
        # Save summary data
        summary_json_path = context.output_dir / "assets" / "data" / "summary_data.json"
        summary_json_path.parent.mkdir(parents=True, exist_ok=True)

        with open(summary_json_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, default=str)
            
        context.data["summary_data"] = summary_data
