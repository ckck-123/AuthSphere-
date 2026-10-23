"""权限 Schema"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PermissionCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None


class PermissionOut(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
