from celery import Celery
from config import settings

celery = Celery(
    "fault_watch",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["tasks.error_processing"]
)

celery.autodiscover_tasks()
