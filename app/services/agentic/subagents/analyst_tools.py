"""
Ready-to-use data tools for gym_analyst_agent.
All queries are fixed — no SQL generation by the agent.
Sources: session_logs, routine_exercises (+ exercise name join).
"""

import os
from datetime import date, timedelta

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

load_dotenv()

_db_url = os.environ["DATABASE_URL"].replace("postgresql://", "postgresql+asyncpg://", 1)
_engine = create_async_engine(_db_url, pool_pre_ping=True)
_Session = async_sessionmaker(bind=_engine, expire_on_commit=False)


def _serialize(row: dict) -> dict:
    return {
        k: str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v
        for k, v in row.items()
    }


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
    query = text("""
        SELECT
            ws.date           AS session_date,
            e.name            AS exercise_name,
            sl.set_number,
            sl.actual_reps,
            sl.actual_weight,
            sl.rpe,
            sl.is_skipped
        FROM session_logs sl
        JOIN workout_sessions ws ON ws.id = sl.session_id
        JOIN exercises e         ON e.id  = sl.exercise_id
        WHERE ws.user_id = :user_id
          AND ws.status  = 'completed'
          AND ws.date   >= :since
          AND sl.is_skipped = false
        ORDER BY ws.date DESC, e.name, sl.set_number
    """)
    async with _Session() as session:
        result = await session.execute(query, {"user_id": user_id, "since": since})
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
    query = text("""
        SELECT
            UNNEST(e.primary_muscles)::text          AS muscle_group,
            SUM(sl.actual_reps * sl.actual_weight)   AS total_volume,
            COUNT(sl.id)                             AS total_sets
        FROM session_logs sl
        JOIN workout_sessions ws ON ws.id = sl.session_id
        JOIN exercises e         ON e.id  = sl.exercise_id
        WHERE ws.user_id = :user_id
          AND ws.status  = 'completed'
          AND ws.date   >= :since
          AND sl.is_skipped = false
        GROUP BY muscle_group
        ORDER BY total_volume DESC
    """)
    async with _Session() as session:
        result = await session.execute(query, {"user_id": user_id, "since": since})
        return [_serialize(dict(row)) for row in result.mappings()]


async def get_exercise_prs(user_id: int) -> list[dict]:
    """
    Return the all-time heaviest weight logged per exercise for the user.

    Each row contains: exercise_name, max_weight, reps_at_max, date_achieved.

    Args:
        user_id: Telegram user ID.
    """
    query = text("""
        SELECT DISTINCT ON (e.name)
            e.name                AS exercise_name,
            sl.actual_weight      AS max_weight,
            sl.actual_reps        AS reps_at_max,
            ws.date               AS date_achieved
        FROM session_logs sl
        JOIN workout_sessions ws ON ws.id = sl.session_id
        JOIN exercises e         ON e.id  = sl.exercise_id
        WHERE ws.user_id = :user_id
          AND ws.status  = 'completed'
          AND sl.is_skipped = false
          AND sl.actual_weight IS NOT NULL
        ORDER BY e.name, sl.actual_weight DESC
    """)
    async with _Session() as session:
        result = await session.execute(query, {"user_id": user_id})
        return [_serialize(dict(row)) for row in result.mappings()]


async def get_routine_exercises(user_id: int) -> list[dict]:
    """
    Return all exercises across all routines belonging to the user.

    Each row contains: routine_name, exercise_name, order,
    planned_sets, planned_reps, planned_weight, primary_muscles.

    Args:
        user_id: Telegram user ID.
    """
    query = text("""
        SELECT
            r.name                      AS routine_name,
            e.name                      AS exercise_name,
            re."order",
            re.planned_sets,
            re.planned_reps,
            re.planned_weight,
            e.primary_muscles::text[]   AS primary_muscles
        FROM routine_exercises re
        JOIN routines r  ON r.id = re.routine_id
        JOIN exercises e ON e.id = re.exercise_id
        WHERE r.user_id = :user_id
        ORDER BY r.name, re."order"
    """)
    async with _Session() as session:
        result = await session.execute(query, {"user_id": user_id})
        return [_serialize(dict(row)) for row in result.mappings()]
