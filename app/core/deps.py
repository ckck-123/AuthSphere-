"""
依赖注入：
- get_current_user：从请求头解析 Bearer token，校验黑名单/签名/用户状态，返回当前用户
- require_permission：权限校验，超级管理员放行，否则检查用户所有角色合并的权限
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis import Redis
from sqlalchemy.orm import Session

from app.core.redis import get_redis
from app.core.security import decode_token
from app.db.base import get_db
from app.models import User

# 从 Authorization: Bearer xxx 里取 token
security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> User:
    # 1) 有没有带 token
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录")

    token = credentials.credentials

    # 2) 是否已登出（在黑名单里），Redis 未启动时按未拉黑处理
    try:
        blacklisted = bool(redis.exists(f"blacklist:{token}"))
    except Exception:
        blacklisted = False
    if blacklisted:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token 已失效")

    # 3) 解析 JWT
    payload = decode_token(token)
    if not payload or "user_id" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token 无效或已过期")

    # 4) 查库并校验用户状态
    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已禁用")

    return user


def require_permission(code: str):
    """
    用法：@router.delete("/{id}", dependencies=[Depends(require_permission("user:delete"))])
    或：def endpoint(_, user=Depends(require_permission("user:read")))
    """

    def checker(user: User = Depends(get_current_user)) -> User:
        if user.is_superuser:  # 超管放行
            return user
        # 收集该用户所有角色下的权限编码
        perm_codes = {p.code for role in user.roles for p in role.permissions}
        if code not in perm_codes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=f"无权限：{code}"
            )
        return user

    return checker
