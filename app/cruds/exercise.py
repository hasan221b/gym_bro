from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.cruds.base import CRUDBase
from app.models.exercises import Exercise
from app.models.enums import MuscleGroupEnum, EquipmentEnum


class ExerciseCRUD(CRUDBase[Exercise]):

    async def get_global(self, db: AsyncSession) -> list[Exercise]:
        result = await db.execute(
            select(Exercise).where(Exercise.is_custom == False)
        )
        return result.scalars().all()

    async def get_by_user(self, db: AsyncSession, user_id: int) -> list[Exercise]:
        result = await db.execute(
            select(Exercise).where(Exercise.created_by == user_id)
        )
        return result.scalars().all()

    async def get_by_muscle(self, db: AsyncSession, muscle: MuscleGroupEnum) -> list[Exercise]:
        result = await db.execute(
            select(Exercise).where(Exercise.primary_muscles.contains([muscle]))
        )
        return result.scalars().all()

    async def get_by_equipment(self, db: AsyncSession, equipment: EquipmentEnum) -> list[Exercise]:
        result = await db.execute(
            select(Exercise).where(Exercise.equipment == equipment)
        )
        return result.scalars().all()


exercise_crud = ExerciseCRUD(Exercise)
