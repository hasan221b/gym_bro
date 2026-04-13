from sqlalchemy import String, DateTime, BigInteger, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,       # Telegram user ID — provided by Telegram, not auto-generated
    )
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # Relationships
    custom_exercises = relationship(
        "Exercise",
        back_populates="creator"
    )
    routines = relationship(
        "Routine",
        back_populates="user",
        cascade="all, delete-orphan"    # user deleted → routines deleted
    )
    sessions = relationship(
        "WorkoutSession",
        back_populates="user",
        cascade="all, delete-orphan"    # user deleted → sessions deleted
    )
    body_metrics = relationship(
        "UserBodyMetric",
        back_populates="user",
        cascade="all, delete-orphan"
    )


