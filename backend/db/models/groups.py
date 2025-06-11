from db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, Text, TIMESTAMP, func
from datetime import datetime

class ErrorGroup(Base):
    __tablename__ = "error_groups"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    fingerprint: Mapped[str] = mapped_column(Text, unique=True, nullable=False, index=True)
    service: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    example_message: Mapped[str] = mapped_column(Text, nullable=False)
    first_seen: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    last_seen: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    occurrences: Mapped[int] = mapped_column(BigInteger, nullable=False, default=1)