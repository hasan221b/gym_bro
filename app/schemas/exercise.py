import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.models.enums import ForceEnum, LevelEnum, MuscleGroupEnum, EquipmentEnum


class ExerciseCreate(BaseModel):
    name: str
    force: Optional[ForceEnum] = None
    level: LevelEnum
    primary_muscles: list[MuscleGroupEnum]
    secondary_muscles: Optional[list[MuscleGroupEnum]] = None
    equipment: Optional[EquipmentEnum] = None
    instructions: Optional[str] = None
    images: Optional[list[str]] = None


class ExerciseUpdate(BaseModel):
    name: Optional[str] = None
    force: Optional[ForceEnum] = None
    level: Optional[LevelEnum] = None
    primary_muscles: Optional[list[MuscleGroupEnum]] = None
    secondary_muscles: Optional[list[MuscleGroupEnum]] = None
    equipment: Optional[EquipmentEnum] = None
    instructions: Optional[str] = None
    images: Optional[list[str]] = None


class ExerciseResponse(BaseModel):
    id: uuid.UUID
    name: str
    force: Optional[ForceEnum]
    level: LevelEnum
    primary_muscles: list[MuscleGroupEnum]
    secondary_muscles: Optional[list[MuscleGroupEnum]]
    equipment: Optional[EquipmentEnum]
    instructions: Optional[str]
    images: Optional[list[str]]
    is_custom: bool
    created_by: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}
