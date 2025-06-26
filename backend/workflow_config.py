import os

def get_settings():
    """
    Get settings from environment variables.
    This function is workflow-safe as it only uses os.environ.
    """
    return {
        "database_url": os.environ["DATABASE_URL"],
        "redis_url": os.environ["REDIS_URL"],
        "temporal_host_port": os.environ.get("TEMPORAL_HOST_PORT", "temporal:7233"),
        "temporal_namespace": os.environ.get("TEMPORAL_NAMESPACE", "default"),
        "temporal_task_queue": os.environ.get("TEMPORAL_TASK_QUEUE", "error-processing"),
    } 