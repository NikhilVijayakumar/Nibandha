from pathlib import Path
from typing import Optional, Dict
from pydantic import BaseModel, Field

class ReportingConfig(BaseModel):
    """
    Configuration for the Reporting Module.
    """
    output_dir: Path = Field(..., description="Directory where reports will be generated")
    docs_dir: Path = Field(..., description="Directory containing test documentation scenarios")
    template_dir: Optional[Path] = Field(None, description="Optional directory for custom templates")
    doc_paths: Dict[str, Path] = Field(
        default_factory=lambda: {
            "functional": Path("docs/modules"), 
            "technical": Path("docs/technical"), 
            "test": Path("docs/test")
        },
        description="Map of documentation categories to paths"
    )

    class Config:
        frozen = True
