import uuid
from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Text, Integer, BigInteger, ForeignKey, TIMESTAMP, DATE, func, DateTime
from sqlalchemy.dialects.postgresql import UUID, ENUM as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import SessionStatusEnum


session_status_enum = PgEnum(
    SessionStatusEnum,
    name="session_status_enum",
    create_type=True
)


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

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
    routine_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("routines.id", ondelete="SET NULL"),  # keep session history even if routine deleted
        nullable=True
    )
    status: Mapped[SessionStatusEnum] = mapped_column(
        session_status_enum,
        nullable=False,
        default=SessionStatusEnum.in_progress
    )
    date: Mapped[date] = mapped_column(
        DATE,
        nullable=False,
        default=date.today
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True                   # set when user starts the session
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True                   # set when session is completed or cancelled
    )
    duration_minutes: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True                   # auto-calculated from started_at/ended_at, or manually entered
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
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

    # Relationships
    user = relationship(
        "User",
        back_populates="sessions"
    )
    routine = relationship(
        "Routine",
        back_populates="sessions"
    )
    session_logs = relationship(
        "SessionLog",
        back_populates="session",
        cascade="all, delete-orphan",   # logs deleted with session
        order_by="SessionLog.set_number"
    )