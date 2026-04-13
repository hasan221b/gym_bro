import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.cruds.base import CRUDBase
from app.models.session_log import SessionLog


class SessionLogCRUD(CRUDBase[SessionLog]):

    async def get_by_session(self, db: AsyncSession, session_id: uuid.UUID) -> list[SessionLog]:
        result = await db.execute(
            select(SessionLog)
            .where(SessionLog.session_id == session_id)
            .order_by(SessionLog.set_number)
        )
        return result.scalars().all()

    async def get_by_exercise(self, db: AsyncSession, exercise_id: uuid.UUID) -> list[SessionLog]:
        result = await db.execute(
            select(SessionLog)
            .where(SessionLog.exercise_id == exercise_id)
        )
        return result.scalars().all()


session_log_crud = SessionLogCRUD(SessionLog)
