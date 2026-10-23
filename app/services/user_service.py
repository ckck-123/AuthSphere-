"""
用户业务：登录校验、增删改查。
这里同时演示了两个技术点：
1. Redis 缓存用户列表，30 秒过期，写操作时主动清缓存
2. 操作日志通过消息队列异步投递，不阻塞接口
"""
import json
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.redis import redis_client
from app.core.security import hash_password, verify_password
from app.models import Role, User
from app.schemas.user import UserCreate, UserUpdate
from app.tasks.producer import push_operation_log

USERS_CACHE_PREFIX = "users:"


# ========== 缓存辅助 ==========
def _cache_key(page: int, page_size: int, keyword: Optional[str]) -> str:
    return f"{USERS_CACHE_PREFIX}{page}:{page_size}:{keyword or ''}"


def _invalidate_users_cache() -> None:
    try:
        for k in redis_client.scan_iter(f"{USERS_CACHE_PREFIX}*"):
            redis_client.delete(k)
    except Exception:
        pass  # Redis 未启动时忽略


# ========== 查询 ==========
def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def list_users(db: Session, page: int, page_size: int, keyword: Optional[str]) -> dict:
    key = _cache_key(page, page_size, keyword)

    # 1) 命中缓存直接返回
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)

    # 2) 未命中查库
    query = db.query(User)
    if keyword:
        query = query.filter(User.username.like(f"%{keyword}%"))
    total = query.count()
    items = (
        query.order_by(User.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    data = {
        "total": total,
        "items": [u.to_dict() for u in items],
    }
    # 3) 写缓存（default=str 处理 datetime）
    redis_client.setex(key, 30, json.dumps(data, ensure_ascii=False, default=str))
    return data


# ========== 校验登录 ==========
def authenticate(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(db, username)
    if user and verify_password(password, user.password_hash):
        return user
    return None


# ========== 增删改 ==========
def create_user(db: Session, data: UserCreate) -> User:
    if get_user_by_username(db, data.username):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "用户名已存在")

    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        nickname=data.nickname,
        email=data.email,
    )
    if data.role_ids:  # 分配角色
        roles = db.query(Role).filter(Role.id.in_(data.role_ids)).all()
        user.roles = roles

    db.add(user)
    db.commit()
    db.refresh(user)
    _invalidate_users_cache()
    return user


def update_user(db: Session, user: User, data: UserUpdate) -> User:
    if data.nickname is not None:
        user.nickname = data.nickname
    if data.email is not None:
        user.email = data.email
    if data.password:
        user.password_hash = hash_password(data.password)
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.role_ids is not None:  # 传了才整体替换角色
        user.roles = db.query(Role).filter(Role.id.in_(data.role_ids)).all()

    db.commit()
    db.refresh(user)
    _invalidate_users_cache()
    return user


def delete_user(db: Session, user: User) -> None:
    if user.is_superuser:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "不允许删除超级管理员")
    db.delete(user)
    db.commit()
    _invalidate_users_cache()
