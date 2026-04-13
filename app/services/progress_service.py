from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid

from app.models.session import WorkoutSession
from app.models.session_log import SessionLog
from app.models.exercises import Exercise
from app.models.body_metric import UserBodyMetric
from app.models.enums import SessionStatusEnum
from app.cruds.body_metric import body_metric_crud
from app.schemas.progress import (
    ExerciseProgressPoint,
    ExerciseProgressResponse,
    WorkoutFrequencyPoint,
    WorkoutFrequencyResponse,
    MuscleGroupVolumePoint,
    MuscleGroupVolumeResponse,
    BodyMetricPoint,
    BodyMetricTrendResponse,
    SummaryResponse,
    CalendarResponse,
)


async def get_exercise_progress(
    db: AsyncSession,
    user_id: int,
    exercise_id: uuid.UUID,
    start_date: date,
    end_date: date,
) -> ExerciseProgressResponse:
    # Fetch exercise name
    exercise = await db.get(Exercise, exercise_id)

    # Get all logs for this exercise within sessions belonging to the user in date range
    result = await db.execute(
        select(
            WorkoutSession.date,
            func.max(SessionLog.actual_weight).label("max_weight"),
            func.sum(SessionLog.actual_reps * SessionLog.actual_weight).label("total_volume"),
            func.count(SessionLog.id).label("total_sets"),
        )
        .join(WorkoutSession, SessionLog.session_id == WorkoutSession.id)
        .where(WorkoutSession.user_id == user_id)
        .where(SessionLog.exercise_id == exercise_id)
        .where(WorkoutSession.date >= start_date)
        .where(WorkoutSession.date <= end_date)
        .where(SessionLog.is_skipped == False)
        .group_by(WorkoutSession.date)
        .order_by(WorkoutSession.date)
    )
    rows = result.all()

    return ExerciseProgressResponse(
        exercise_id=exercise_id,
        exercise_name=exercise.name if exercise else "Unknown",
        data=[
            ExerciseProgressPoint(
                period_start=row.date,
                max_weight=row.max_weight,
                total_volume=row.total_volume or 0,
                total_sets=row.total_sets,
            )
            for row in rows
        ],
    )


async def get_workout_frequency(
    db: AsyncSession,
    user_id: int,
    start_date: date,
    end_date: date,
) -> WorkoutFrequencyResponse:
    result = await db.execute(
        select(
            WorkoutSession.date,
            func.count(WorkoutSession.id).label("session_count"),
            func.sum(SessionLog.actual_reps * SessionLog.actual_weight).label("total_volume"),
        )
        .join(SessionLog, SessionLog.session_id == WorkoutSession.id, isouter=True)
        .where(WorkoutSession.user_id == user_id)
        .where(WorkoutSession.date >= start_date)
        .where(WorkoutSession.date <= end_date)
        .where(SessionLog.is_skipped == False)
        .group_by(WorkoutSession.date)
        .order_by(WorkoutSession.date)
    )
    rows = result.all()

    return WorkoutFrequencyResponse(
        data=[
            WorkoutFrequencyPoint(
                period_start=row.date,
                session_count=row.session_count,
                total_volume=row.total_volume or 0,
            )
            for row in rows
        ]
    )


async def get_muscle_group_volume(
    db: AsyncSession,
    user_id: int,
    start_date: date,
    end_date: date,
) -> MuscleGroupVolumeResponse:
    # Get all logs with their exercise's primary muscles
    result = await db.execute(
        select(
            Exercise.primary_muscles,
            func.sum(SessionLog.actual_reps * SessionLog.actual_weight).label("total_volume"),
            func.count(SessionLog.id).label("total_sets"),
        )
        .join(WorkoutSession, SessionLog.session_id == WorkoutSession.id)
        .join(Exercise, SessionLog.exercise_id == Exercise.id)
        .where(WorkoutSession.user_id == user_id)
        .where(WorkoutSession.date >= start_date)
        .where(WorkoutSession.date <= end_date)
        .where(SessionLog.is_skipped == False)
        .group_by(Exercise.primary_muscles)
    )
    rows = result.all()

    # Flatten — one exercise can have multiple primary muscles
    muscle_volume: dict = {}
    muscle_sets: dict = {}
    for row in rows:
        for muscle in row.primary_muscles:
            muscle_volume[muscle] = muscle_volume.get(muscle, 0) + (row.total_volume or 0)
            muscle_sets[muscle] = muscle_sets.get(muscle, 0) + row.total_sets

    return MuscleGroupVolumeResponse(
        start_date=start_date,
        end_date=end_date,
        data=[
            MuscleGroupVolumePoint(
                muscle_group=muscle,
                total_volume=volume,
                total_sets=muscle_sets[muscle],
            )
            for muscle, volume in muscle_volume.items()
        ],
    )


async def get_summary(
    db: AsyncSession,
    user_id: int,
    start_date: date,
    end_date: date,
) -> SummaryResponse:
    # Total completed sessions in period
    sessions_result = await db.execute(
        select(func.count(WorkoutSession.id))
        .where(WorkoutSession.user_id == user_id)
        .where(WorkoutSession.date >= start_date)
        .where(WorkoutSession.date <= end_date)
        .where(WorkoutSession.status == SessionStatusEnum.completed)
    )
    total_sessions = sessions_result.scalar() or 0

    # Total volume in period
    volume_result = await db.execute(
        select(func.sum(SessionLog.actual_reps * SessionLog.actual_weight))
        .join(WorkoutSession, SessionLog.session_id == WorkoutSession.id)
        .where(WorkoutSession.user_id == user_id)
        .where(WorkoutSession.date >= start_date)
        .where(WorkoutSession.date <= end_date)
        .where(SessionLog.is_skipped == False)
    )
    total_volume = volume_result.scalar() or 0

    # Current streak — all-time workout dates, calculate consecutive days from today
    dates_result = await db.execute(
        select(WorkoutSession.date)
        .where(WorkoutSession.user_id == user_id)
        .where(WorkoutSession.status == SessionStatusEnum.completed)
        .group_by(WorkoutSession.date)
        .order_by(WorkoutSession.date.desc())
    )
    workout_date_set = {row[0] for row in dates_result.all()}

    today = date.today()
    streak = 0
    check = today if today in workout_date_set else today - timedelta(days=1)
    while check in workout_date_set:
        streak += 1
        check -= timedelta(days=1)

    return SummaryResponse(
        total_sessions=total_sessions,
        total_volume=float(total_volume),
        current_streak=streak,
    )


async def get_workout_calendar(
    db: AsyncSession,
    user_id: int,
    start_date: date,
    end_date: date,
) -> CalendarResponse:
    result = await db.execute(
        select(WorkoutSession.date)
        .where(WorkoutSession.user_id == user_id)
        .where(WorkoutSession.date >= start_date)
        .where(WorkoutSession.date <= end_date)
        .where(WorkoutSession.status == SessionStatusEnum.completed)
        .group_by(WorkoutSession.date)
        .order_by(WorkoutSession.date)
    )
    return CalendarResponse(workout_dates=[row[0] for row in result.all()])


async def get_body_metric_trend(
    db: AsyncSession,
    user_id: int,
    start_date: date,
    end_date: date,
) -> BodyMetricTrendResponse:
    metrics = await body_metric_crud.get_by_user_and_date_range(db, user_id, start_date, end_date)

    return BodyMetricTrendResponse(
        data=[
            BodyMetricPoint(
                recorded_at=m.recorded_at,
                weight_kg=m.weight_kg,
                body_fat_pct=m.body_fat_pct,
            )
            for m in metrics
        ]
    )
