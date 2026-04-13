import uuid
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.progress import (
    ExerciseProgressResponse,
    WorkoutFrequencyResponse,
    MuscleGroupVolumeResponse,
    BodyMetricTrendResponse,
    SummaryResponse,
    CalendarResponse,
)
from app.schemas.body_metric import BodyMetricCreate, BodyMetricResponse
from app.services.progress_service import (
    get_exercise_progress,
    get_workout_frequency,
    get_muscle_group_volume,
    get_body_metric_trend,
    get_summary,
    get_workout_calendar,
)
from app.cruds.body_metric import body_metric_crud

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.get("/summary", response_model=SummaryResponse)
async def summary(
    user_id: int = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
):
    return await get_summary(db, user_id, start_date, end_date)


@router.get("/calendar", response_model=CalendarResponse)
async def workout_calendar(
    user_id: int = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
):
    return await get_workout_calendar(db, user_id, start_date, end_date)


@router.get("/exercise/{exercise_id}", response_model=ExerciseProgressResponse)
async def exercise_progress(
    exercise_id: uuid.UUID,
    user_id: int = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
):
    return await get_exercise_progress(db, user_id, exercise_id, start_date, end_date)


@router.get("/frequency", response_model=WorkoutFrequencyResponse)
async def workout_frequency(
    user_id: int = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
):
    return await get_workout_frequency(db, user_id, start_date, end_date)


@router.get("/muscles", response_model=MuscleGroupVolumeResponse)
async def muscle_group_volume(
    user_id: int = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
):
    return await get_muscle_group_volume(db, user_id, start_date, end_date)


@router.get("/body", response_model=BodyMetricTrendResponse)
async def body_metric_trend(
    user_id: int = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
):
    return await get_body_metric_trend(db, user_id, start_date, end_date)


@router.post("/body", response_model=BodyMetricResponse, status_code=201)
async def log_body_metric(
    user_id: int = Query(...),
    data: BodyMetricCreate = ...,
    db: AsyncSession = Depends(get_db),
):
    return await body_metric_crud.create(db, {
        "user_id": user_id,
        "weight_kg": data.weight_kg,
        "body_fat_pct": data.body_fat_pct,
    })
