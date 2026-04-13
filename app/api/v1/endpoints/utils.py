from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy import text

from app.db.database import get_db

router = APIRouter(prefix="/utils", tags=["Utils"])


@router.delete("/reset", status_code=200)
async def reset_data(db: AsyncSession = Depends(get_db)):
    """Delete all data from all tables except exercises."""
    await db.execute(text("""
        TRUNCATE TABLE
            session_logs,
            workout_sessions,
            routine_exercises,
            routines,
            user_body_metrics,
            users
        RESTART IDENTITY
    """))
    await db.commit()
    return {"detail": "All data cleared except exercises"}
