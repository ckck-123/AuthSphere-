"""
用户管理接口：分页列表 / 详情 / 新增 / 修改 / 删除。
每个写操作都用权限依赖做鉴权，并把操作日志投递到消息队列。
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_permission
from app.db.base import get_db
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.services import user_service
from app.tasks.producer import push_operation_log
from app.utils.response import ApiResponse, ok

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get(
    "",
    response_model=ApiResponse,
    summary="用户列表（带 Redis 缓存）",
    dependencies=[Depends(require_permission("user:read"))],
)
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = Query(None, description="按用户名模糊搜索"),
    db: Session = Depends(get_db),
):
    return ok(user_service.list_users(db, page, page_size, keyword))


@router.post(
    "",
    response_model=ApiResponse,
    summary="新增用户",
    dependencies=[Depends(require_permission("user:create"))],
)
def create_user(data: UserCreate, db: Session = Depends(get_db), admin=Depends(get_current_user)):
    user = user_service.create_user(db, data)
    push_operation_log(admin.id, admin.username, "user_create", f"创建用户 {user.username}")
    return ok(UserOut.model_validate(user), "创建成功")


@router.get(
    "/{user_id}",
    response_model=ApiResponse,
    summary="用户详情",
    dependencies=[Depends(require_permission("user:read"))],
)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "用户不存在")
    return ok(UserOut.model_validate(user))


@router.put(
    "/{user_id}",
    response_model=ApiResponse,
    summary="修改用户",
    dependencies=[Depends(require_permission("user:update"))],
)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_user),
):
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "用户不存在")
    user = user_service.update_user(db, user, data)
    push_operation_log(admin.id, admin.username, "user_update", f"修改用户 {user.username}")
    return ok(UserOut.model_validate(user), "修改成功")


@router.delete(
    "/{user_id}",
    response_model=ApiResponse,
    summary="删除用户",
    dependencies=[Depends(require_permission("user:delete"))],
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_user),
):
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "用户不存在")
    username = user.username
    user_service.delete_user(db, user)
    push_operation_log(admin.id, admin.username, "user_delete", f"删除用户 {username}")
    return ok(message="删除成功")
