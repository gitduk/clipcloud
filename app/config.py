import os


class Config:
    # Basic config
    DEBUG = False

    # Flask redis
    REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")

    # Celery
    CELERY = {
        "broker_url": os.environ.get("BROKER_URL", "redis://127.0.0.1:6379/2"),
        "result_backend": os.environ.get("RESULT_BACKEND", "redis://127.0.0.1:6379/1"),

        "timezone": "Asia/Shanghai",
        "enable_utc": False,

        "worker_concurrency": 1,
        "worker_max_tasks_per_child": 10,

        "broker_connection_retry_on_startup": True,

        "accept_content": ["json"],
        "task_serializer": "json",
        "result_serializer": "json"
    }


config = {
    "default": Config
}

