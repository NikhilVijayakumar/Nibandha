from pathlib import Path
from typing import Optional, Dict, TYPE_CHECKING, List
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from ...reporting.shared.domain.protocols.module_discovery import ModuleDiscoveryProtocol

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
    module_discovery: Optional["ModuleDiscoveryProtocol"] = Field(
        None,
        description="Optional custom module discovery protocol for flexible architecture support"
    )
    export_formats: List[str] = Field(
        default=["md"],
        description="List of formats to export reports to (e.g. ['md', 'html', 'docx'])"
    )

    class Config:
        frozen = True
