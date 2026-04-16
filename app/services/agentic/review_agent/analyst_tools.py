"""
Ready-to-use data tools for gym_analyst_agent.
All queries are fixed — no SQL generation by the agent.
Sources: session_logs, routine_exercises (+ exercise name join).
"""

from datetime import date, timedelta

from sqlalchemy import String, func, select

from app.db.database import SessionLocal
from app.models.enums import SessionStatusEnum
from app.models.exercises import Exercise
from app.models.routine_exercise import RoutineExercise
from app.models.routines import Routine
from app.models.session import WorkoutSession
from app.models.session_log import SessionLog
from app.models.body_metric import UserBodyMetric

def _serialize(row: dict) -> dict:
    result = {}
    for k, v in row.items():
        if isinstance(v, list):
            result[k] = [
                i if isinstance(i, (str, int, float, bool, type(None))) else str(i)
                for i in v
            ]
        elif isinstance(v, (str, int, float, bool, type(None))):
            result[k] = v
        else:
            result[k] = str(v)
    return result


async def get_user_session_logs(user_id: int, days: int = 30) -> list[dict]:
    """
    Return all logged sets for the user in the last N days.

    Each row contains: session_date, exercise_name, set_number,
    actual_reps, actual_weight, rpe, is_skipped.

    Args:
        user_id: Telegram user ID.
        days:    How many days back to look (default 30).
    """
    since = date.today() - timedelta(days=days)

    stmt = (
        select(
            WorkoutSession.date.label("session_date"),
            Exercise.name.label("exercise_name"),
            SessionLog.set_number,
            SessionLog.actual_reps,
            SessionLog.actual_weight,
            SessionLog.rpe,
            SessionLog.is_skipped,
        )
        .join(WorkoutSession, WorkoutSession.id == SessionLog.session_id)
        .join(Exercise, Exercise.id == SessionLog.exercise_id)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == SessionStatusEnum.completed,
            WorkoutSession.date >= since,
            SessionLog.is_skipped == False,
        )
        .order_by(WorkoutSession.date.desc(), Exercise.name, SessionLog.set_number)
    )

    async with SessionLocal() as session:
        result = await session.execute(stmt)
        return [_serialize(dict(row)) for row in result.mappings()]


async def get_volume_by_muscle(user_id: int, days: int = 30) -> list[dict]:
    """
    Return total volume (actual_reps × actual_weight) and total sets
    grouped by primary muscle group for the last N days.

    Each row contains: muscle_group, total_volume, total_sets.

    Args:
        user_id: Telegram user ID.
        days:    How many days back to look (default 30).
    """
    since = date.today() - timedelta(days=days)

    muscle_group = func.unnest(Exercise.primary_muscles).cast(String).label("muscle_group")
    total_volume = func.sum(SessionLog.actual_reps * SessionLog.actual_weight).label("total_volume")
    total_sets   = func.count(SessionLog.id).label("total_sets")

    stmt = (
        select(muscle_group, total_volume, total_sets)
        .join(WorkoutSession, WorkoutSession.id == SessionLog.session_id)
        .join(Exercise, Exercise.id == SessionLog.exercise_id)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == SessionStatusEnum.completed,
            WorkoutSession.date >= since,
            SessionLog.is_skipped == False,
        )
        .group_by(func.unnest(Exercise.primary_muscles).cast(String))
        .order_by(total_volume.desc())
    )

    async with SessionLocal() as session:
        result = await session.execute(stmt)
        return [_serialize(dict(row)) for row in result.mappings()]


async def get_exercise_prs(user_id: int) -> list[dict]:
    """
    Return the all-time heaviest weight logged per exercise for the user.

    Each row contains: exercise_name, max_weight, reps_at_max, date_achieved.

    Args:
        user_id: Telegram user ID.
    """
    stmt = (
        select(
            Exercise.name.label("exercise_name"),
            SessionLog.actual_weight.label("max_weight"),
            SessionLog.actual_reps.label("reps_at_max"),
            WorkoutSession.date.label("date_achieved"),
        )
        .distinct(Exercise.name)
        .join(WorkoutSession, WorkoutSession.id == SessionLog.session_id)
        .join(Exercise, Exercise.id == SessionLog.exercise_id)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == SessionStatusEnum.completed,
            SessionLog.is_skipped == False,
            SessionLog.actual_weight.is_not(None),
        )
        .order_by(Exercise.name, SessionLog.actual_weight.desc())
    )

    async with SessionLocal() as session:
        result = await session.execute(stmt)
        return [_serialize(dict(row)) for row in result.mappings()]


async def get_routine_exercises(user_id: int) -> list[dict]:
    """
    Return all exercises across all routines belonging to the user.

    Each row contains: routine_name, exercise_name, order,
    planned_sets, planned_reps, planned_weight, primary_muscles.

    Args:
        user_id: Telegram user ID.
    """
    stmt = (
        select(
            Routine.name.label("routine_name"),
            Exercise.name.label("exercise_name"),
            RoutineExercise.order,
            RoutineExercise.planned_sets,
            RoutineExercise.planned_reps,
            RoutineExercise.planned_weight,
            Exercise.primary_muscles,
        )
        .join(Routine, Routine.id == RoutineExercise.routine_id)
        .join(Exercise, Exercise.id == RoutineExercise.exercise_id)
        .where(Routine.user_id == user_id)
        .order_by(Routine.name, RoutineExercise.order)
    )

    async with SessionLocal() as session:
        result = await session.execute(stmt)
        return [_serialize(dict(row)) for row in result.mappings()]


async def get_body_metrics(user_id: int, days: int = 30) -> list[dict]:
    """
    Return the user's body metrics (weight, body fat %) for the last N days.

    Each row contains: recorded_at, weight_kg, body_fat_pct.

    Args:
        user_id: Telegram user ID.
        days:    How many days back to look (default 30).
    """
    since = date.today() - timedelta(days=days)
    stmt = (
        select(
            UserBodyMetric.recorded_at,
            UserBodyMetric.weight_kg,
            UserBodyMetric.age,
            UserBodyMetric.height_cm,
            UserBodyMetric.body_fat_pct,
        )
        .where(
            UserBodyMetric.user_id == user_id,
            UserBodyMetric.recorded_at >= since,
        )
        .order_by(UserBodyMetric.recorded_at.desc())
    )
    async with SessionLocal() as session:
        result = await session.execute(stmt)
        return [_serialize(dict(row)) for row in result.mappings()]


async def get_avg_session_duration(user_id: int, days: int = 30) -> dict:
    """
    Return the average session duration in minutes for the user's completed
    sessions in the last N days, along with the total session count used
    in the calculation.

    Result contains: avg_duration_minutes, total_sessions, period_days.

    Args:
        user_id: Telegram user ID.
        days:    How many days back to look (default 30).
    """
    since = date.today() - timedelta(days=days)

    stmt = (
        select(
            func.round(func.avg(WorkoutSession.duration_minutes), 1).label("avg_duration_minutes"),
            func.count(WorkoutSession.id).label("total_sessions"),
        )
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == SessionStatusEnum.completed,
            WorkoutSession.date >= since,
            WorkoutSession.duration_minutes.is_not(None),
        )
    )

    async with SessionLocal() as session:
        result = await session.execute(stmt)
        row = result.mappings().one()
        return _serialize(dict(row)) | {"period_days": days}
