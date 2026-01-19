from nibandha.domain.models.base_config import NibandhaBaseConfig
from pydantic import Field

class ArchiverSettings(NibandhaBaseConfig):
    # No Hardcoding: Defaults are defined in the schema
    compression_level: int = Field(default=9, ge=0, le=9)
    workspace_path: str = Field(description="[AR-UT-007] Must be provided by Loader")