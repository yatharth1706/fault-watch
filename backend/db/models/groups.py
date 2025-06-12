from db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, Text, TIMESTAMP, String, func, Index
from datetime import datetime
from enum import Enum


class GroupStatus(str, Enum):
    UNRESOLVED = "unresolved"
    RESOLVED = "resolved"
    IGNORED = "ignored"


class ErrorGroup(Base):
    __tablename__ = "error_groups"
    
    # Fingerprinting
    fingerprint: Mapped[str] = mapped_column(Text, unique=True, nullable=False, index=True)
    grouping_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Project and environment
    service: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    environment: Mapped[str] = mapped_column(String(100), nullable=False, default="production", index=True)
    
    # Error details
    title: Mapped[str] = mapped_column(Text, nullable=False)
    culprit: Mapped[str] = mapped_column(Text, nullable=True)
    level: Mapped[str] = mapped_column(String(20), nullable=False, default="error")
    
    # Status and tracking
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=GroupStatus.UNRESOLVED)
    first_seen: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    last_seen: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    occurrences: Mapped[int] = mapped_column(BigInteger, nullable=False, default=1)
    
    # User impact (MVP: basic tracking)
    users_affected: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    
    # Legacy field for backward compatibility
    example_message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_service_env_status', 'service', 'environment', 'status'),
        Index('idx_fingerprint_status', 'fingerprint', 'status'),
        Index('idx_last_seen_status', 'last_seen', 'status'),
    )