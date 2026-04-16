import uuid
from datetime import date, datetime
from typing import Optional
from sqlalchemy import Float, Integer, BigInteger, ForeignKey, TIMESTAMP, DATE, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class UserBodyMetric(Base):
    __tablename__ = "user_body_metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    recorded_at: Mapped[date] = mapped_column(
        DATE,
        nullable=False,
        default=date.today         # one entry per day is the typical pattern
    )
    weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    body_fat_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="body_metrics")
