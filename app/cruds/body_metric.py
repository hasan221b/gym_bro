from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.cruds.base import CRUDBase
from app.models.body_metric import UserBodyMetric


class BodyMetricCRUD(CRUDBase[UserBodyMetric]):

    async def get_by_user(self, db: AsyncSession, user_id: int) -> list[UserBodyMetric]:
        result = await db.execute(
            select(UserBodyMetric)
            .where(UserBodyMetric.user_id == user_id)
            .order_by(UserBodyMetric.recorded_at.desc())
        )
        return result.scalars().all()

    async def get_by_user_and_date_range(
        self,
        db: AsyncSession,
        user_id: int,
        start_date: date,
        end_date: date
    ) -> list[UserBodyMetric]:
        result = await db.execute(
            select(UserBodyMetric)
            .where(UserBodyMetric.user_id == user_id)
            .where(UserBodyMetric.recorded_at >= start_date)
            .where(UserBodyMetric.recorded_at <= end_date)
            .order_by(UserBodyMetric.recorded_at.desc())
        )
        return result.scalars().all()


body_metric_crud = BodyMetricCRUD(UserBodyMetric)
