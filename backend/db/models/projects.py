from datetime import datetime
from sqlalchemy import String, Integer, Boolean, TIMESTAMP, func, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base


class Project(Base):
    __tablename__ = "projects"
        
    # Organization relationship
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    organization = relationship("Organization", back_populates="projects")
    
    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    platform: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Settings
    retention_days: Mapped[int] = mapped_column(Integer, nullable=False, server_default="90")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    
    # Relationships
    api_keys = relationship("APIKey", back_populates="project", cascade="all, delete-orphan")
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_project_org_id', 'organization_id'),
        Index('idx_project_slug', 'slug'),
        # Ensure unique slug per organization
        {'unique_constraints': [('organization_id', 'slug')]}
    ) 