from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    temporal_host_port: str = "temporal:7233"
    temporal_namespace: str = "default"
    temporal_task_queue: str = "error-processing"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()