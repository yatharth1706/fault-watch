from datetime import datetime
from sqlalchemy import String, Boolean, TIMESTAMP, ForeignKey, Integer, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base


class APIKey(Base):
    __tablename__ = "api_keys"
    
    # Project relationship
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    project = relationship("Project", back_populates="api_keys")
    
    # Key details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    prefix: Mapped[str] = mapped_column(String(8), nullable=False)  # First 8 chars of key for reference
    key_hash: Mapped[str] = mapped_column(String(128), nullable=False)  # Hashed API key
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    last_used_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_api_key_project', 'project_id'),
        Index('idx_api_key_prefix', 'prefix'),
        Index('idx_api_key_active', 'is_active'),
    ) 