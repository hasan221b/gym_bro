import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, BigInteger, Text, ForeignKey, TIMESTAMP, UniqueConstraint, Index, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY, ENUM as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import ForceEnum, LevelEnum, MuscleGroupEnum, EquipmentEnum


# PostgreSQL native enum types
# These are defined once at the DB level and reused across columns
force_enum = PgEnum(ForceEnum, name="force_enum", create_type=True)
level_enum = PgEnum(LevelEnum, name="level_enum", create_type=True)
muscle_group_enum = PgEnum(MuscleGroupEnum, name="muscle_group_enum", create_type=True)
equipment_enum = PgEnum(EquipmentEnum, name="equipment_enum", create_type=True)


class Exercise(Base):
    __tablename__ = "exercises"
    __table_args__ = (
        # Global exercises (created_by IS NULL) are unique by name.
        # Custom exercises are unique per user — same name allowed across users.
        UniqueConstraint("name", "created_by", name="uq_exercise_name_creator"),
        # Speed up the most common query patterns
        Index("ix_exercises_is_custom", "is_custom"),
        Index("ix_exercises_equipment", "equipment"),
        Index("ix_exercises_created_by", "created_by"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    force: Mapped[Optional[ForceEnum]] = mapped_column(force_enum, nullable=True)
    level: Mapped[LevelEnum] = mapped_column(level_enum, nullable=False)
    primary_muscles: Mapped[list[MuscleGroupEnum]] = mapped_column(ARRAY(muscle_group_enum), nullable=False)
    secondary_muscles: Mapped[Optional[list[MuscleGroupEnum]]] = mapped_column(ARRAY(muscle_group_enum), nullable=True)
    equipment: Mapped[Optional[EquipmentEnum]] = mapped_column(equipment_enum, nullable=True)
    instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    images: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    creator = relationship("User", back_populates="custom_exercises")
    routine_exercises = relationship("RoutineExercise", back_populates="exercise")
    session_logs = relationship("SessionLog", back_populates="exercise")
