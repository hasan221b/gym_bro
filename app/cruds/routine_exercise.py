from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import uuid

from app.cruds.base import CRUDBase
from app.models.routine_exercise import RoutineExercise


class RoutineExerciseCRUD(CRUDBase[RoutineExercise]):

    async def get_with_exercise(self, db: AsyncSession, id: uuid.UUID) -> RoutineExercise | None:
        result = await db.execute(
            select(RoutineExercise)
            .where(RoutineExercise.id == id)
            .options(selectinload(RoutineExercise.exercise))
        )
        return result.scalar_one_or_none()

    async def get_by_routine(self, db: AsyncSession, routine_id: uuid.UUID) -> list[RoutineExercise]:
        result = await db.execute(
            select(RoutineExercise)
            .where(RoutineExercise.routine_id == routine_id)
            .options(selectinload(RoutineExercise.exercise))
            .order_by(RoutineExercise.order)
        )
        return result.scalars().all()


routine_exercise_crud = RoutineExerciseCRUD(RoutineExercise)
