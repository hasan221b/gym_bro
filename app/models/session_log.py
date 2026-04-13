import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, Float, Boolean, ForeignKey, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID, ENUM as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import SetTypeEnum


set_type_enum = PgEnum(
    SetTypeEnum,
    name="set_type_enum",
    create_type=True
)


class SessionLog(Base):
    __tablename__ = "session_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workout_sessions.id", ondelete="CASCADE"),
        nullable=False
    )
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exercises.id", ondelete="CASCADE"),
        nullable=False
    )
    set_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False                  # 1, 2, 3 ... per exercise per session
    )
    set_type: Mapped[SetTypeEnum] = mapped_column(
        set_type_enum,
        nullable=False,
        default=SetTypeEnum.working     # most sets are working sets
    )
    planned_reps: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True                   # copied from routine_exercise as a reference
    )
    planned_weight: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True                   # copied from routine_exercise as a reference
    )
    actual_reps: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True                   # null if set is skipped
    )
    actual_weight: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True                   # null if skipped or bodyweight exercise
    )
    is_skipped: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    rpe: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True                   # Rate of Perceived Exertion 1-10, logged after the set
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    session = relationship(
        "WorkoutSession",
        back_populates="session_logs"
    )
    exercise = relationship(
        "Exercise",
        back_populates="session_logs"
    )