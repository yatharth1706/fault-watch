from datetime import datetime
from sqlalchemy import TIMESTAMP, BigInteger, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import re


class Base(DeclarativeBase):
    """Enhanced base model with automatic common fields and table naming."""
    
    def __init_subclass__(cls, **kwargs):
        """Automatically set table name if not provided."""
        if not hasattr(cls, '__tablename__'):
            # Convert class name to snake_case
            cls.__tablename__ = cls._to_snake_case(cls.__name__)
        super().__init_subclass__(**kwargs)
    
    @staticmethod
    def _to_snake_case(name: str) -> str:
        """Convert CamelCase to snake_case."""
        # Handle consecutive uppercase letters (like 'API' -> 'api')
        name = re.sub('([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
        # Handle single uppercase letters followed by lowercase
        name = re.sub('([a-z])([A-Z])', r'\1_\2', name)
        return name.lower()
    
    # Common fields that will be automatically included in all models
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(),
        nullable=False
    )

    def model_dump(self, exclude: set = None) -> dict:
        """Convert SQLAlchemy model to dictionary, similar to Pydantic's model_dump()"""
        exclude = exclude or set()
        return {
            k: v for k, v in self.__dict__.items() 
            if not k.startswith('_') and k not in exclude
        }