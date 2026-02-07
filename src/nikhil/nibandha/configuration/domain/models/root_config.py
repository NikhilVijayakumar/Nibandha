from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class RootConfig(BaseModel):
    """
    Configuration for the unified root directory structure.
    """
    name: Optional[str] = Field(None, description="Name of the root directory. If None, it will be auto-discovered from pyproject.toml.")
    custom_structure: Dict[str, Any] = Field(default_factory=dict, description="Dictionary defining custom folder structure (nested). Keys are folder names, values are sub-structure dicts or None.")
