from celery import Celery

from src.core.config import settings


celery_app = Celery(
    "celery_worker",
    broker=settings.redis.get_redis_url,
    backend=settings.redis.get_redis_url,
    include=["src.tasks.tasks"],
)
