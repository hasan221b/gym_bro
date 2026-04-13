import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.cruds.session import session_crud
from app.cruds.session_log import session_log_crud
from app.models.session import WorkoutSession
from app.models.session_log import SessionLog
from app.models.enums import SessionStatusEnum
from app.schemas.session import SessionCreate
from app.schemas.session_log import SessionLogCreate


async def start_session(db: AsyncSession, user_id: int, data: SessionCreate) -> WorkoutSession:
    # Prevent starting a new session if one is already in progress
    active = await session_crud.get_active_session(db, user_id)
    if active:
        raise ValueError("You already have an active session in progress")

    return await session_crud.create(db, {
        "user_id": user_id,
        "routine_id": data.routine_id,
        "notes": data.notes,
        "status": SessionStatusEnum.in_progress,
        "started_at": datetime.now(timezone.utc),
    })


async def log_set(db: AsyncSession, session_id: uuid.UUID, data: SessionLogCreate) -> SessionLog:
    return await session_log_crud.create(db, {
        "session_id": session_id,
        "exercise_id": data.exercise_id,
        "set_number": data.set_number,
        "set_type": data.set_type,
        "planned_reps": data.planned_reps,
        "planned_weight": data.planned_weight,
        "actual_reps": data.actual_reps,
        "actual_weight": data.actual_weight,
        "is_skipped": data.is_skipped,
        "rpe": data.rpe,
    })


async def complete_session(db: AsyncSession, session: WorkoutSession) -> WorkoutSession:
    ended_at = datetime.now(timezone.utc)
    duration = None
    if session.started_at:
        duration = int((ended_at - session.started_at).total_seconds() / 60)

    return await session_crud.update(db, session, {
        "status": SessionStatusEnum.completed,
        "ended_at": ended_at,
        "duration_minutes": duration,
    })


async def cancel_session(db: AsyncSession, session: WorkoutSession) -> WorkoutSession:
    return await session_crud.update(db, session, {
        "status": SessionStatusEnum.cancelled,
        "ended_at": datetime.now(timezone.utc),
    })
