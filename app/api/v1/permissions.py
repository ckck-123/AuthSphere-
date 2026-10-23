"""权限管理接口：列表 / 新增 / 删除"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_permission
from app.db.base import get_db
from app.models import Permission
from app.schemas.permission import PermissionCreate, PermissionOut
from app.services import permission_service
from app.tasks.producer import push_operation_log
from app.utils.response import ApiResponse, ok

router = APIRouter(prefix="/permissions", tags=["权限管理"])


@router.get(
    "",
    response_model=ApiResponse,
    summary="权限列表",
    dependencies=[Depends(require_permission("permission:read"))],
)
def list_permissions(db: Session = Depends(get_db)):
    perms = permission_service.list_permissions(db)
    return ok([PermissionOut.model_validate(p) for p in perms])


@router.post(
    "",
    response_model=ApiResponse,
    summary="新增权限",
    dependencies=[Depends(require_permission("permission:create"))],
)
def create_permission(data: PermissionCreate, db: Session = Depends(get_db), admin=Depends(get_current_user)):
    perm = permission_service.create_permission(db, data)
    push_operation_log(admin.id, admin.username, "permission_create", f"创建权限 {perm.code}")
    return ok(PermissionOut.model_validate(perm), "创建成功")


@router.delete(
    "/{permission_id}",
    response_model=ApiResponse,
    summary="删除权限",
    dependencies=[Depends(require_permission("permission:delete"))],
)
def delete_permission(permission_id: int, db: Session = Depends(get_db), admin=Depends(get_current_user)):
    perm = db.get(Permission, permission_id)
    if not perm:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "权限不存在")
    permission_service.delete_permission(db, perm)
    push_operation_log(admin.id, admin.username, "permission_delete", f"删除权限 {perm.code}")
    return ok(message="删除成功")
