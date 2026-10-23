"""角色业务：增删改查 + 分配权限"""
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Permission, Role
from app.schemas.role import RoleCreate, RoleUpdate


def get_role(db: Session, role_id: int) -> Optional[Role]:
    return db.query(Role).filter(Role.id == role_id).first()


def get_role_by_code(db: Session, code: str) -> Optional[Role]:
    return db.query(Role).filter(Role.code == code).first()


def list_roles(db: Session) -> List[Role]:
    return db.query(Role).order_by(Role.id).all()


def create_role(db: Session, data: RoleCreate) -> Role:
    if get_role_by_code(db, data.code):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "角色编码已存在")

    role = Role(name=data.name, code=data.code, description=data.description)
    if data.permission_ids:
        role.permissions = (
            db.query(Permission).filter(Permission.id.in_(data.permission_ids)).all()
        )
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def update_role(db: Session, role: Role, data: RoleUpdate) -> Role:
    if data.name is not None:
        role.name = data.name
    if data.description is not None:
        role.description = data.description
    if data.permission_ids is not None:  # 传了才整体替换权限
        role.permissions = (
            db.query(Permission).filter(Permission.id.in_(data.permission_ids)).all()
        )
    db.commit()
    db.refresh(role)
    return role


def delete_role(db: Session, role: Role) -> None:
    if role.code == "admin":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "不允许删除内置管理员角色")
    db.delete(role)
    db.commit()
