import uuid
from datetime import datetime, date  # date kept for SessionResponse
from typing import Optional
from pydantic import BaseModel

from app.models.enums import SessionStatusEnum

from app.schemas.session_log import SessionLogResponse


class SessionCreate(BaseModel):
    routine_id: Optional[uuid.UUID] = None      # optional: user may do a free workout
    notes: Optional[str] = None


class SessionUpdate(BaseModel):
    status: Optional[SessionStatusEnum] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None


class SessionResponse(BaseModel):
    id: uuid.UUID
    user_id: int
    routine_id: Optional[uuid.UUID]
    status: SessionStatusEnum
    date: date
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    duration_minutes: Optional[int]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SessionDetailResponse(SessionResponse):
    session_logs: list[SessionLogResponse] = []
