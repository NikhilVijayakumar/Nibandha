from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class UnifiedRootConfig(BaseModel):
    """Configuration for the unified root directory structure."""
    name: Optional[str] = Field(None, description="Name of the root directory")
    custom_structure: Dict[str, Any] = Field(default_factory=dict, description="Custom folder structure")
