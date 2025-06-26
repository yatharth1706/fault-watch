import os

class TemporalSettings:
    host_port: str = os.environ.get("TEMPORAL_HOST_PORT", "temporal:7233")
    namespace: str = os.environ.get("TEMPORAL_NAMESPACE", "default")
    task_queue: str = os.environ.get("TEMPORAL_TASK_QUEUE", "error-processing")

temporal_settings = TemporalSettings() 