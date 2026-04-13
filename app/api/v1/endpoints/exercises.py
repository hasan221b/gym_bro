from typing import Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.cruds.exercise import exercise_crud
from app.models.enums import MuscleGroupEnum, EquipmentEnum
from app.schemas.exercise import ExerciseCreate, ExerciseUpdate, ExerciseResponse

router = APIRouter(prefix="/exercises", tags=["Exercises"])


@router.get("", response_model=list[ExerciseResponse])
async def get_exercises(
    muscle: Optional[MuscleGroupEnum] = Query(default=None),
    equipment: Optional[EquipmentEnum] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    if muscle:
        return await exercise_crud.get_by_muscle(db, muscle)
    if equipment:
        return await exercise_crud.get_by_equipment(db, equipment)
    return await exercise_crud.get_global(db)


@router.get("/user/{user_id}", response_model=list[ExerciseResponse])
async def get_user_exercises(user_id: int, db: AsyncSession = Depends(get_db)):
    return await exercise_crud.get_by_user(db, user_id)


@router.get("/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise(exercise_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    exercise = await exercise_crud.get(db, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise


@router.post("", status_code=201, response_model=ExerciseResponse)
async def create_exercise(data: ExerciseCreate, user_id: int, db: AsyncSession = Depends(get_db)):
    return await exercise_crud.create(db, {
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


@router.patch("/{exercise_id}", response_model=ExerciseResponse)
async def update_exercise(
    exercise_id: uuid.UUID,
    data: ExerciseUpdate,
    db: AsyncSession = Depends(get_db)
):
    exercise = await exercise_crud.get(db, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return await exercise_crud.update(db, exercise, data.model_dump(exclude_unset=True))


@router.delete("/{exercise_id}", status_code=204)
async def delete_exercise(exercise_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    exercise = await exercise_crud.get(db, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    await exercise_crud.delete(db, exercise)
