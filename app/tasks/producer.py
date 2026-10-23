"""
生产者：把一条"操作日志"消息投递到队列。
调用方（service/api）只负责塞消息，真正写库由消费者异步完成，
这就是消息队列解耦的意义——接口不用等落库。
Redis 没启动时静默降级，不影响主流程。
"""
from typing import Optional

from app.core.config import settings
from app.core.redis import redis_client
from app.tasks.queue import enqueue


def push_operation_log(
    user_id: Optional[int],
    username: str,
    action: str,
    detail: str = "",
) -> None:
    message = {
        "user_id": user_id,
        "username": username,
        "action": action,
        "detail": detail,
    }
    try:
        enqueue(redis_client, settings.QUEUE_NAME, message)
    except Exception as e:  # Redis 未启动时静默降级
        print(f"[producer] Redis 不可用，跳过日志投递: {e}")
