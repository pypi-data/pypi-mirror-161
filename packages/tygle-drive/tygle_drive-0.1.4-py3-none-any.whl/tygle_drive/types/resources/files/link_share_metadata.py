from typing import Optional

from pydantic import BaseModel, Field


class LinkShareMetadata(BaseModel):
    security_update_eligible: Optional[bool] = Field(
        None, alias="securityUpdateEligible"
    )
    security_update_enabled: Optional[bool] = Field(None, alias="securityUpdateEnabled")
