"""
数据库引擎 / 会话 / Base 基类。
- engine：连接池，负责和 MySQL 通信
- SessionLocal：生产会话的工厂，每个请求一个会话
- Base：所有 ORM 模型的基类，建表靠它
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    """所有模型的基类"""


# pool_pre_ping=True：取连接前先探活，避免 MySQL 断线导致报错
engine = create_engine(settings.db_url, pool_pre_ping=True, echo=False)

# autocommit=False：显式 commit，防止意外把半成品写进库
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    """
    依赖注入：FastAPI 每个请求自动调用，
    结束后自动关会话，不用手动 close。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
