from datetime import datetime
from sqlalchemy import JSON, TIMESTAMP, Boolean, Text, String, func, Index
from db.base import Base
from sqlalchemy.orm import Mapped, mapped_column


class RawError(Base):
    __tablename__ = "raw_errors"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Project and environment
    service: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    environment: Mapped[str] = mapped_column(String(100), nullable=False, default="production", index=True)
    
    # Error details
    message: Mapped[str] = mapped_column(Text, nullable=False)
    level: Mapped[str] = mapped_column(String(20), nullable=False, default="error")
    
    # Exception information
    exception_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    exception_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    exception_module: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Context
    tags: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    extra: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    # User context
    user_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    user_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    user_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    user_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    
    # Request context
    request_method: Mapped[str | None] = mapped_column(String(10), nullable=True)
    request_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    request_headers: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    request_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    # Metadata
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    received_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    release: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # Processing flags
    processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Legacy fields for backward compatibility
    error_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    stack_trace: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_service_env_timestamp', 'service', 'environment', 'timestamp'),
        Index('idx_level_timestamp', 'level', 'timestamp'),
    )