"""
模型统一出口：导入所有模型，让 create_all 能发现全部表。
"""
from app.models.association import role_permissions, user_roles
from app.models.operation_log import OperationLog
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User

__all__ = ["User", "Role", "Permission", "OperationLog", "user_roles", "role_permissions"]
