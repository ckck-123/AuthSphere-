"""角色 Schema"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.schemas.permission import PermissionOut


class RoleCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    permission_ids: List[int] = []  # 创建时可指定权限


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[List[int]] = None  # 传了则整体替换权限


class RoleOut(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    created_at: datetime
    permissions: List[PermissionOut] = []

    model_config = {"from_attributes": True}
