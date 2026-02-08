from typing import List, Optional, Dict
from pathlib import Path
from pydantic import BaseModel, Field, field_serializer, field_validator

class ExportConfig(BaseModel):
    """Configuration for export settings."""
    formats: List[str] = Field(default=["md", "html"], description="Export formats")
    style: str = Field("default", description="CSS/Theme style name")
    
    # Input/Output directories
    input_dir: Optional[Path] = Field(None, description="Directory containing source markdown files to export")
    template_dir: Optional[Path] = Field(None, description="Custom template directory")
    styles_dir: Optional[Path] = Field(None, description="Directory containing CSS style files")
    output_dir: Optional[Path] = Field(None, description="Directory to save exported files")
    output_filename: str = Field("report", description="Base filename for exported files (without extension)")
    
    # File control
    export_order: Optional[List[str]] = Field(
        None, 
        description="Custom order for markdown files (filenames without extension). If None, uses alphabetic order."
    )
    exclude_files: List[str] = Field(
        default_factory=list,
        description="List of filenames (without extension) to exclude from export. Applies to all formats."
    )
    
    # Metrics mapping
    metrics_mapping: Dict[str, str] = Field(
        default_factory=dict,
        description="Mapping of report filenames to JSON data filenames. Example: {'unit_report': 'unit'}"
    )
    
    # Serialize Path fields to POSIX format (forward slashes) for cross-platform compatibility
    @field_serializer('input_dir', 'template_dir', 'styles_dir', 'output_dir')
    def serialize_path(self, path: Optional[Path], _info) -> Optional[str]:
        """Convert Path to POSIX-style string (forward slashes)."""
        return path.as_posix() if path else None
    
    @field_validator('export_order', mode='before')
    @classmethod
    def validate_export_order(cls, v):
        """Ensure export_order doesn't contain excluded files."""
        # Validation happens after both fields are set, so we can't cross-check here
        # This is just for basic type validation
        return v
