import uuid
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.cruds.base import CRUDBase
from app.models.session import WorkoutSession
from app.models.enums import SessionStatusEnum


class SessionCRUD(CRUDBase[WorkoutSession]):

    async def get_with_logs(self, db: AsyncSession, session_id: uuid.UUID) -> WorkoutSession | None:
        result = await db.execute(
            select(WorkoutSession)
            .where(WorkoutSession.id == session_id)
            .options(selectinload(WorkoutSession.session_logs))
        )
        return result.scalar_one_or_none()

    async def get_by_user(self, db: AsyncSession, user_id: int) -> list[WorkoutSession]:
        result = await db.execute(
            select(WorkoutSession)
            .where(WorkoutSession.user_id == user_id)
            .order_by(WorkoutSession.date.desc())
        )
        return result.scalars().all()

    async def get_by_user_and_date_range(
        self,
        db: AsyncSession,
        user_id: int,
        start_date: date,
        end_date: date
    ) -> list[WorkoutSession]:
        result = await db.execute(
            select(WorkoutSession)
            .where(WorkoutSession.user_id == user_id)
            .where(WorkoutSession.date >= start_date)
            .where(WorkoutSession.date <= end_date)
            .order_by(WorkoutSession.date.desc())
        )
        return result.scalars().all()

    async def get_active_session(self, db: AsyncSession, user_id: int) -> WorkoutSession | None:
        result = await db.execute(
            select(WorkoutSession)
            .where(WorkoutSession.user_id == user_id)
            .where(WorkoutSession.status == SessionStatusEnum.in_progress)
        )
        return result.scalars().first()


session_crud = SessionCRUD(WorkoutSession)
