"""Celery app configuration."""
# Import the Celery app
from .main import celery

# Make it available at the package level
__all__ = ['celery']
