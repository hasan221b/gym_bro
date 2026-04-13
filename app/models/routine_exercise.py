import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Boolean, Integer, Float, ForeignKey, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

class RoutineExercise(Base):
    __tablename__ = "routine_exercises"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    routine_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("routines.id", ondelete="CASCADE"),
        nullable=False
    )
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exercises.id", ondelete="CASCADE"),
        nullable=False
    )
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=1)          # position in the routine (1, 2, 3 ...)
    planned_sets: Mapped[int] = mapped_column(Integer, nullable=False)
    planned_reps: Mapped[int] = mapped_column(Integer, nullable=False)              # target reps per set e.g. 10
    planned_weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)   # nullable for bodyweight exercises
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)        # e.g. "pause at bottom", "slow eccentric"

    # Relationships
    routine = relationship("Routine", back_populates="routine_exercises")
    exercise = relationship("Exercise", back_populates="routine_exercises")
