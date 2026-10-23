"""角色管理接口：列表 / 新增 / 修改 / 删除"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_permission
from app.db.base import get_db
from app.schemas.role import RoleCreate, RoleOut, RoleUpdate
from app.services import role_service
from app.tasks.producer import push_operation_log
from app.utils.response import ApiResponse, ok

router = APIRouter(prefix="/roles", tags=["角色管理"])


@router.get(
    "",
    response_model=ApiResponse,
    summary="角色列表",
    dependencies=[Depends(require_permission("role:read"))],
)
def list_roles(db: Session = Depends(get_db)):
    roles = role_service.list_roles(db)
    return ok([RoleOut.model_validate(r) for r in roles])


@router.post(
    "",
    response_model=ApiResponse,
    summary="新增角色",
    dependencies=[Depends(require_permission("role:create"))],
)
def create_role(data: RoleCreate, db: Session = Depends(get_db), admin=Depends(get_current_user)):
    role = role_service.create_role(db, data)
    push_operation_log(admin.id, admin.username, "role_create", f"创建角色 {role.name}")
    return ok(RoleOut.model_validate(role), "创建成功")


@router.put(
    "/{role_id}",
    response_model=ApiResponse,
    summary="修改角色（可整体替换权限）",
    dependencies=[Depends(require_permission("role:update"))],
)
def update_role(
    role_id: int,
    data: RoleUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_user),
):
    role = role_service.get_role(db, role_id)
    if not role:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "角色不存在")
    role = role_service.update_role(db, role, data)
    push_operation_log(admin.id, admin.username, "role_update", f"修改角色 {role.name}")
    return ok(RoleOut.model_validate(role), "修改成功")


@router.delete(
    "/{role_id}",
    response_model=ApiResponse,
    summary="删除角色",
    dependencies=[Depends(require_permission("role:delete"))],
)
def delete_role(role_id: int, db: Session = Depends(get_db), admin=Depends(get_current_user)):
    role = role_service.get_role(db, role_id)
    if not role:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "角色不存在")
    role_service.delete_role(db, role)
    push_operation_log(admin.id, admin.username, "role_delete", f"删除角色 {role.name}")
    return ok(message="删除成功")
