import uuid
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, model_validator


class BodyMetricCreate(BaseModel):
    weight_kg: Optional[float] = None
    body_fat_pct: Optional[float] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None

    @model_validator(mode="after")
    def at_least_one_field(self):
        if self.weight_kg is None and self.body_fat_pct is None:
            raise ValueError("Provide at least weight_kg or body_fat_pct")
        return self


class BodyMetricResponse(BaseModel):
    id: uuid.UUID
    user_id: int
    recorded_at: date
    weight_kg: Optional[float]
    body_fat_pct: Optional[float]
    age: Optional[int]
    height_cm: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}
