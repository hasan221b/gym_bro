import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.schemas.routine_exercise import RoutineExerciseResponse


class RoutineCreate(BaseModel):
    name: str
    description: Optional[str] = None


class RoutineUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class RoutineResponse(BaseModel):
    id: uuid.UUID
    user_id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RoutineDetailResponse(RoutineResponse):
    routine_exercises: list[RoutineExerciseResponse] = []
