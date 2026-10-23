"""
队列底层封装。
原理：用 Redis 的 List 结构做消息队列。
- 生产者 rpush 往队尾放消息
- 消费者 blpop 从队头阻塞取消息（取不到就等着，不占CPU）
"""
import json
from typing import Optional

from redis import Redis


def enqueue(redis: Redis, queue_name: str, message: dict) -> None:
    """生产：往队列里放一条消息"""
    redis.rpush(queue_name, json.dumps(message, ensure_ascii=False))


def dequeue(redis: Redis, queue_name: str, timeout: int = 0) -> Optional[dict]:
    """消费：从队列取一条消息，timeout 秒内没消息就返回 None（timeout=0 表示一直等）"""
    item = redis.blpop(queue_name, timeout=timeout)
    if item is None:
        return None
    _queue, payload = item
    return json.loads(payload)
