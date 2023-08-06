from datetime import datetime
from typing import ClassVar, Dict, Optional

from pydantic import BaseModel, Field

from .user import User


class ContentRestriction(BaseModel):
    read_only: Optional[bool] = Field(None, alias="readOnly")
    reason: Optional[str] = Field(None)
    restricting_user: Optional[User] = Field(None, alias="restrictingUser")
    restriction_time: Optional[datetime] = Field(None, alias="restrictionTime")
    type: Optional[str] = Field(None)
