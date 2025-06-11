from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    database_url: str
    redis_url: str

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        extra = "ignore"  # Ignore extra fields from .env

settings = Settings()