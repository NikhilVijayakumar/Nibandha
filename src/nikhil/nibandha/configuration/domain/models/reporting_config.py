from pathlib import Path
from typing import Optional, Dict, TYPE_CHECKING, List
from pydantic import BaseModel, Field, ConfigDict

if TYPE_CHECKING:
    from nibandha.reporting.shared.domain.protocols.module_discovery import ModuleDiscoveryProtocol

class ReportingConfig(BaseModel):
    """
    Configuration for the Reporting Module.
    """
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
    
    # Directories (Can be inferred from App Context if None)
    output_dir: Optional[Path] = Field(None, description="Directory where reports will be generated")
    docs_dir: Optional[Path] = Field(None, description="Directory containing test documentation scenarios")
    template_dir: Optional[Path] = Field(None, description="Optional directory for custom templates")
    
    # Project Metadata
    project_name: str = Field("Nibandha", description="Name of the project")
    
    # Analysis Targets
    quality_target: str = Field("src", description="Target directory/package for quality checks")
    package_roots: List[str] = Field(default=[], description="List of package roots for dependency analysis")
    unit_target: str = Field("tests/unit", description="Target directory for unit tests")
    e2e_target: str = Field("tests/e2e", description="Target directory for E2E tests")
    
    doc_paths: Dict[str, Path] = Field(
        default_factory=lambda: {
            "functional": Path("docs/features"), 
            "technical": Path("docs/technical"), 
            "test": Path("docs/test")
        },
        description="Map of documentation categories to paths"
    )
    module_discovery: Optional["ModuleDiscoveryProtocol"] = Field(
        None,
        description="Optional custom module discovery protocol"
    )
    export_formats: List[str] = Field(
        default=["md"],
        description="List of formats to export reports to (e.g. ['md', 'html', 'docx'])"
    )
