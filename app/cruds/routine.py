import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.cruds.base import CRUDBase
from app.models.routines import Routine
from app.models.routine_exercise import RoutineExercise


class RoutineCRUD(CRUDBase[Routine]):

    async def get_with_exercises(self, db: AsyncSession, routine_id: uuid.UUID) -> Routine | None:
        result = await db.execute(
            select(Routine)
            .where(Routine.id == routine_id)
            .options(
                selectinload(Routine.routine_exercises)
                .selectinload(RoutineExercise.exercise)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user(self, db: AsyncSession, user_id: int) -> list[Routine]:
        result = await db.execute(
            select(Routine).where(Routine.user_id == user_id)
        )
        return result.scalars().all()

    async def get_active_by_user(self, db: AsyncSession, user_id: int) -> list[Routine]:
        result = await db.execute(
            select(Routine)
            .where(Routine.user_id == user_id)
            .where(Routine.is_active == True)
        )
        return result.scalars().all()


routine_crud = RoutineCRUD(Routine)
