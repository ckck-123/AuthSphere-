"""
初始化脚本：建表 + 写入种子数据（默认权限、admin 角色、admin 用户）。
运行方式（在 backend 目录下）：
    python -m app.db.init_db

初始账号：admin / admin123
"""
import app.models  # noqa: F401  确保所有模型先注册，create_all 才能发现表
from app.core.security import hash_password
from app.db.base import Base, SessionLocal, engine
from app.models import Permission, Role, User

# 系统内置权限（可按需增删）
DEFAULT_PERMISSIONS = [
    ("查看用户", "user:read"),
    ("创建用户", "user:create"),
    ("修改用户", "user:update"),
    ("删除用户", "user:delete"),
    ("查看角色", "role:read"),
    ("创建角色", "role:create"),
    ("修改角色", "role:update"),
    ("删除角色", "role:delete"),
    ("查看权限", "permission:read"),
]


def init_db() -> None:
    # 1) 建表
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # 2) 权限：不存在才插入
        perm_map = {}
        for name, code in DEFAULT_PERMISSIONS:
            perm = db.query(Permission).filter_by(code=code).first()
            if not perm:
                perm = Permission(name=name, code=code, description=name)
                db.add(perm)
            perm_map[code] = perm
        db.commit()

        # 3) admin 角色：拥有全部权限
        admin_role = db.query(Role).filter_by(code="admin").first()
        if not admin_role:
            admin_role = Role(name="管理员", code="admin", description="拥有所有权限")
            db.add(admin_role)
            db.flush()
        admin_role.permissions = list(perm_map.values())

        # 4) admin 用户：超级管理员，挂到 admin 角色
        admin_user = db.query(User).filter_by(username="admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                password_hash=hash_password("admin123"),
                nickname="超级管理员",
                is_active=True,
                is_superuser=True,
            )
            db.add(admin_user)
            db.flush()
        if admin_role not in admin_user.roles:
            admin_user.roles.append(admin_role)

        db.commit()
        print("✅ 初始化完成，初始账号：admin / admin123")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
