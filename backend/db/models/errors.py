from datetime import datetime
from sqlalchemy import JSON, TIMESTAMP, Boolean, Text, func
from db.base import Base
from sqlalchemy.orm import Mapped, mapped_column


class RawError(Base):
    received_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    service: Mapped[str] = mapped_column(Text)
    error_type: Mapped[str | None] = mapped_column(Text)
    message: Mapped[str] = mapped_column(Text)
    stack_trace: Mapped[str | None] = mapped_column(Text) 
    error_metadata: Mapped[dict | None] = mapped_column(JSON)
    processed: Mapped[bool] = mapped_column(Boolean, default=False)