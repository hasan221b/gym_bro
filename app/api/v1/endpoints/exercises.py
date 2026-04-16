from typing import Optional
import uuid
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.cruds.exercise import exercise_crud
from app.models.enums import MuscleGroupEnum, EquipmentEnum
from app.schemas.exercise import ExerciseCreate, ExerciseUpdate, ExerciseResponse
from app.core.cache import cache

router = APIRouter(prefix="/exercises", tags=["Exercises"])

# How long exercise lists stay cached (1 hour)
_LIST_TTL = 3600
# How long a single exercise stays cached (24 hours)
_ITEM_TTL = 86400


def _serialize_list(exercises) -> str:
    """Convert ORM Exercise objects → JSON string via Pydantic."""
    return json.dumps([
        ExerciseResponse.model_validate(e).model_dump(mode="json")
        for e in exercises
    ])


async def _invalidate(exercise, user_id=None, exercise_id=None):
    """Delete every cache key that could contain this exercise."""
    keys = ["exercises:global"]
    if user_id:
        keys.append(f"exercises:user:{user_id}")
    if exercise.equipment:
        keys.append(f"exercises:equipment:{exercise.equipment.value}")
    for muscle in (exercise.primary_muscles or []):
        keys.append(f"exercises:muscle:{muscle.value}")
    if exercise_id:
        keys.append(f"exercise:{exercise_id}")
    await cache.delete(*keys)


# ── READ ──────────────────────────────────────────────────────────────────────

@router.get("", response_model=list[ExerciseResponse])
async def get_exercises(
    muscle: Optional[MuscleGroupEnum] = Query(default=None),
    equipment: Optional[EquipmentEnum] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    # Build a unique cache key based on the filter being applied
    if muscle:
        cache_key = f"exercises:muscle:{muscle.value}"
    elif equipment:
        cache_key = f"exercises:equipment:{equipment.value}"
    else:
        cache_key = "exercises:global"

    # Cache hit → return immediately without touching the DB
    cached = await cache.get(cache_key)
    if cached:
        return json.loads(cached)

    # Cache miss → query DB, then store result for next time
    if muscle:
        exercises = await exercise_crud.get_by_muscle(db, muscle)
    elif equipment:
        exercises = await exercise_crud.get_by_equipment(db, equipment)
    else:
        exercises = await exercise_crud.get_global(db)

    await cache.set(cache_key, _serialize_list(exercises), ex=_LIST_TTL)
    return exercises


@router.get("/user/{user_id}", response_model=list[ExerciseResponse])
async def get_user_exercises(user_id: int, db: AsyncSession = Depends(get_db)):
    cache_key = f"exercises:user:{user_id}"

    cached = await cache.get(cache_key)
    if cached:
        return json.loads(cached)

    exercises = await exercise_crud.get_by_user(db, user_id)
    await cache.set(cache_key, _serialize_list(exercises), ex=_LIST_TTL)
    return exercises


@router.get("/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise(exercise_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    cache_key = f"exercise:{exercise_id}"

    cached = await cache.get(cache_key)
    if cached:
        return json.loads(cached)

    exercise = await exercise_crud.get(db, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    data = ExerciseResponse.model_validate(exercise).model_dump(mode="json")
    await cache.set(cache_key, json.dumps(data), ex=_ITEM_TTL)
    return exercise


# ── WRITE (invalidate cache on every mutation) ────────────────────────────────

@router.post("", status_code=201, response_model=ExerciseResponse)
async def create_exercise(data: ExerciseCreate, user_id: int, db: AsyncSession = Depends(get_db)):
    exercise = await exercise_crud.create(db, {
        "name": data.name,
        "force": data.force,
        "level": data.level,
        "primary_muscles": data.primary_muscles,
        "secondary_muscles": data.secondary_muscles,
        "equipment": data.equipment,
        "instructions": data.instructions,
        "images": data.images,
        "is_custom": True,
        "created_by": user_id,
    })
    await _invalidate(exercise, user_id=user_id)
    return exercise


@router.patch("/{exercise_id}", response_model=ExerciseResponse)
async def update_exercise(
    exercise_id: uuid.UUID,
    data: ExerciseUpdate,
    db: AsyncSession = Depends(get_db)
):
    exercise = await exercise_crud.get(db, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    updated = await exercise_crud.update(db, exercise, data.model_dump(exclude_unset=True))
    await _invalidate(updated, user_id=updated.created_by, exercise_id=exercise_id)
    return updated


@router.delete("/{exercise_id}", status_code=204)
async def delete_exercise(exercise_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    exercise = await exercise_crud.get(db, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    await exercise_crud.delete(db, exercise)
    await _invalidate(exercise, user_id=exercise.created_by, exercise_id=exercise_id)
