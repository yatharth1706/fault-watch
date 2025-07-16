from db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, TIMESTAMP, String, func, Index, Integer, ForeignKey, Float
from datetime import datetime
from enum import Enum
from .projects import Project


class GroupStatus(str, Enum):
    UNRESOLVED = "unresolved"
    RESOLVED = "resolved"
    IGNORED = "ignored"


class ErrorGroup(Base):
    __tablename__ = "error_groups"
    
    # Project relationship
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey('projects.id'), nullable=False)
    project: Mapped[Project] = relationship("Project", backref="error_groups")
    
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
    
    # Assignment and ownership
    assigned_to: Mapped[int | None] = mapped_column(Integer, nullable=True)
    resolved_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    ignored_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ignored_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    last_assigned_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    
    # User impact metrics
    users_affected: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    last_user_seen: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    unique_users_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    avg_events_per_day: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Legacy field for backward compatibility
    example_message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_service_env_status', 'service', 'environment', 'status'),
        Index('idx_fingerprint_status', 'fingerprint', 'status'),
        Index('idx_last_seen_status', 'last_seen', 'status'),
        Index('idx_error_groups_project_status', 'project_id', 'status'),
    )