import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.enums import SetTypeEnum


class SessionLogCreate(BaseModel):
    exercise_id: uuid.UUID
    set_number: int
    set_type: SetTypeEnum = SetTypeEnum.working
    planned_reps: Optional[int] = None
    planned_weight: Optional[float] = None
    actual_reps: Optional[int] = None
    actual_weight: Optional[float] = None
    is_skipped: bool = False
    rpe: Optional[int] = Field(default=None, ge=1, le=10)   # must be 1-10 if provided


class SessionLogUpdate(BaseModel):
    actual_reps: Optional[int] = None
    actual_weight: Optional[float] = None
    is_skipped: Optional[bool] = None
    rpe: Optional[int] = Field(default=None, ge=1)


class SessionLogResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    exercise_id: uuid.UUID
    set_number: int
    set_type: SetTypeEnum
    planned_reps: Optional[int]
    planned_weight: Optional[float]
    actual_reps: Optional[int]
    actual_weight: Optional[float]
    is_skipped: bool
    rpe: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}
