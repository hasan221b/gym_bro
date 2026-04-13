import uuid
from typing import Optional
from pydantic import BaseModel

from app.schemas.exercise import ExerciseResponse


class RoutineExerciseCreate(BaseModel):
    exercise_id: uuid.UUID
    planned_sets: int
    planned_reps: int
    planned_weight: Optional[float] = None
    notes: Optional[str] = None


class RoutineExerciseUpdate(BaseModel):
    order: Optional[int] = None
    planned_sets: Optional[int] = None
    planned_reps: Optional[int] = None
    planned_weight: Optional[float] = None
    notes: Optional[str] = None


class RoutineExerciseResponse(BaseModel):
    id: uuid.UUID
    routine_id: uuid.UUID
    exercise_id: uuid.UUID
    order: int
    planned_sets: int
    planned_reps: int
    planned_weight: Optional[float]
    notes: Optional[str]
    exercise: ExerciseResponse         # nested — full exercise details

    model_config = {"from_attributes": True}
