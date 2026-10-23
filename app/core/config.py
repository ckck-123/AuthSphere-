"""
全局配置：从 .env 读取。
pydantic-settings 会自动把 .env 里的字段注入到 Settings 类，
字段名要和 .env 里的键一致（大小写不敏感）。
"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend 根目录：config.py 在 backend/app/core/ 下，往上3级
BASE_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ===== 数据库 =====
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "123456"
    DB_NAME: str = "fastapi_admin"

    # ===== Redis =====
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    # ===== JWT =====
    SECRET_KEY: str = "change-me-to-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # token 有效期(分钟)，默认1天

    # ===== 消息队列(基于 Redis List) =====
    QUEUE_NAME: str = "queue:operation_log"

    @property
    def db_url(self) -> str:
        """拼出 SQLAlchemy 连接串"""
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )


settings = Settings()
