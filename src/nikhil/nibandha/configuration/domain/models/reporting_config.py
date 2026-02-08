from pathlib import Path
from typing import Optional, Dict, List, Any, Union
from pydantic import BaseModel, Field, ConfigDict, field_serializer

class ReportingConfig(BaseModel):
    """Configuration for the Reporting Module."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Directories
    output_dir: Optional[Path] = Field(None, description="Directory where reports will be generated")
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
    module_discovery: Optional[Union[List[str], Any]] = Field(
        None,
        description="Optional custom module discovery protocol (Object) or static list of modules (List[str])"
    )

    # Serialize all Path fields to POSIX format (forward slashes) for cross-platform compatibility
    @field_serializer('output_dir', 'template_dir')
    def serialize_path(self, path: Optional[Path], _info) -> Optional[str]:
        """Convert Path to POSIX-style string (forward slashes)."""
        return path.as_posix() if path else None
    
    @field_serializer('doc_paths')
    def serialize_doc_paths(self, paths: Dict[str, Path], _info) -> Dict[str, str]:
        """Convert all doc_paths to POSIX-style strings."""
        return {key: val.as_posix() for key, val in paths.items()}
