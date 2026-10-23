"""
认证接口：登录 / 登出 / 查看当前用户。
登出通过 Redis 黑名单让 token 立即失效，这是 Redis 在认证里最典型的用法。
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from redis import Redis
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user, security
from app.core.redis import get_redis
from app.core.security import create_access_token
from app.db.base import get_db
from app.schemas.user import LoginRequest, UserOut
from app.services import user_service
from app.tasks.producer import push_operation_log
from app.utils.response import ApiResponse, ok

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=ApiResponse, summary="登录")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    user = user_service.authenticate(db, data.username, data.password)
    if not user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "账号已被禁用")

    token = create_access_token({"user_id": user.id})
    push_operation_log(user.id, user.username, "login", "用户登录成功")
    return ok(
        {
            "access_token": token,
            "token_type": "bearer",
            "user": UserOut.model_validate(user),
        },
        "登录成功",
    )


@router.post("/logout", response_model=ApiResponse, summary="登出")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user=Depends(get_current_user),
    redis: Redis = Depends(get_redis),
):
    token = credentials.credentials
    # 把 token 加入黑名单，过期时间 = token 剩余有效时长
    try:
        redis.setex(f"blacklist:{token}", settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, "1")
    except Exception:
        pass
    push_operation_log(user.id, user.username, "logout", "用户登出")
    return ok(message="登出成功")


@router.get("/me", response_model=ApiResponse, summary="当前登录用户信息")
def me(user=Depends(get_current_user)):
    return ok(UserOut.model_validate(user))
