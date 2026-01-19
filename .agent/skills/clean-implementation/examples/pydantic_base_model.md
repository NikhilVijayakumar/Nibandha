This template ensures all settings models follow the Immutability (Frozen) and Strict Type rules from the Constitution.

Python

from pydantic import BaseModel, ConfigDict, Field

class NibandhaBaseSettings(BaseModel):
    """
    Standard Base for all Settings.
    - Frozen: Ensures no runtime tampering.
    - Strict: Prevents type coercion (e.g., '1' becomes 1).
    """
    model_config = ConfigDict(
        frozen=True,
        strict=True,
        extra='forbid'
    )

# Example Usage for Agent:
# class RotationSettings(NibandhaBaseSettings):
#     max_age_days: int = Field(gt=0, description="[AR-UT-008] Traceability ID")