"""权限业务：列表、新增、删除"""
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Permission
from app.schemas.permission import PermissionCreate


def get_permission_by_code(db: Session, code: str) -> Optional[Permission]:
    return db.query(Permission).filter(Permission.code == code).first()


def list_permissions(db: Session) -> List[Permission]:
    return db.query(Permission).order_by(Permission.id).all()


def create_permission(db: Session, data: PermissionCreate) -> Permission:
    if get_permission_by_code(db, data.code):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "权限编码已存在")
    perm = Permission(name=data.name, code=data.code, description=data.description)
    db.add(perm)
    db.commit()
    db.refresh(perm)
    return perm


def delete_permission(db: Session, permission: Permission) -> None:
    db.delete(permission)
    db.commit()
