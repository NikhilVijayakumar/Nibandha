from pathlib import Path
from typing import Optional
from nibandha.reporting.shared.rendering.template_engine import TemplateEngine

class IntroductionReporter:
    def __init__(self, output_dir: Path, templates_dir: Path, template_engine: Optional[TemplateEngine] = None):
        self.output_dir = output_dir
        self.templates_dir = templates_dir
        self.details_dir = output_dir / "details"
        self.details_dir.mkdir(parents=True, exist_ok=True)
        self.template_engine = template_engine or TemplateEngine(templates_dir)

    def generate(self, project_name: str = "Project", metadata: Optional[dict] = None) -> None:
        target = self.details_dir / "01_introduction.md"
        data = {"project_name": project_name}
        if metadata:
            data.update(metadata)
        self.template_engine.render("introduction_template.md", data, target)
