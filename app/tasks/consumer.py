"""
消费者：独立进程，阻塞读取队列里的操作日志，写入 MySQL。
和生产端彻底分离，启动方式（在 backend 目录下）：
    python -m app.tasks.consumer
"""
from app.core.config import settings
from app.core.redis import redis_client
from app.db.base import SessionLocal
from app.models import OperationLog
from app.tasks.queue import dequeue


def consume_once() -> None:
    """取一条消息并落库"""
    data = dequeue(redis_client, settings.QUEUE_NAME, timeout=1)
    if data is None:
        return

    db = SessionLocal()
    try:
        log = OperationLog(
            user_id=data.get("user_id"),
            username=data.get("username"),
            action=data.get("action"),
            detail=data.get("detail"),
        )
        db.add(log)
        db.commit()
        print(f"✅ 已写入操作日志: {data.get('action')}")
    except Exception as e:
        db.rollback()
        print(f"❌ 日志写入失败: {e}")
    finally:
        db.close()


def run() -> None:
    print(f"🧾 消费者已启动，监听队列: {settings.QUEUE_NAME}")
    while True:
        consume_once()


if __name__ == "__main__":
    run()
