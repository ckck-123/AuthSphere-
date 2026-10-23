"""
Redis 连接：缓存 + token 黑名单 + 消息队列的载体。
"""
import redis

from app.core.config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD or None,
    decode_responses=True,  # 让返回值直接是 str，不用手动 b"" 解码
)


def get_redis() -> redis.Redis:
    """给依赖注入用，方便测试时替换"""
    return redis_client
