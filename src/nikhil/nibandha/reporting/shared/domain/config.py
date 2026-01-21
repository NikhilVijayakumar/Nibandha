from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field

class ReportingConfig(BaseModel):
    """
    Configuration for the Reporting Module.
    """
    output_dir: Path = Field(..., description="Directory where reports will be generated")
    docs_dir: Path = Field(..., description="Directory containing test documentation scenarios")
    template_dir: Optional[Path] = Field(None, description="Optional directory for custom templates")

    class Config:
        frozen = True
