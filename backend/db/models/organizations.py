from datetime import datetime
from sqlalchemy import String, Boolean, TIMESTAMP, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base


class Organization(Base):
    __tablename__ = "organizations"
        
    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    projects = relationship("Project", back_populates="organization", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_org_slug', 'slug'),
        Index('idx_org_created', 'created_at'),
    ) 