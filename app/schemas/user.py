"""用户 Schema"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.role import RoleOut


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="登录名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    nickname: Optional[str] = None
    email: Optional[str] = None
    role_ids: List[int] = []


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role_ids: Optional[List[int]] = None


class UserOut(BaseModel):
    id: int
    username: str
    nickname: Optional[str] = None
    email: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    roles: List[RoleOut] = []

    model_config = {"from_attributes": True}
