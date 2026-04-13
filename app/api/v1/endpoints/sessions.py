import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.cruds.session import session_crud
from app.schemas.session import SessionCreate, SessionResponse, SessionDetailResponse
from app.schemas.session_log import SessionLogCreate, SessionLogResponse
from app.services.session_service import start_session, log_set, complete_session, cancel_session
from app.models.enums import SessionStatusEnum

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("/start", status_code=201, response_model=SessionResponse)
async def start_session_endpoint(
    user_id: int,
    data: SessionCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await start_session(db, user_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    session = await session_crud.get_with_logs(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/{session_id}/log", status_code=201, response_model=SessionLogResponse)
async def log_set_endpoint(
    session_id: uuid.UUID,
    data: SessionLogCreate,
    db: AsyncSession = Depends(get_db)
):
    session = await session_crud.get(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != SessionStatusEnum.in_progress:
        raise HTTPException(status_code=400, detail="Session is not in progress")
    return await log_set(db, session_id, data)


@router.post("/{session_id}/complete", response_model=SessionResponse)
async def complete_session_endpoint(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    session = await session_crud.get(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != SessionStatusEnum.in_progress:
        raise HTTPException(status_code=400, detail="Session is not in progress")
    return await complete_session(db, session)


@router.post("/{session_id}/cancel", response_model=SessionResponse)
async def cancel_session_endpoint(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    session = await session_crud.get(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != SessionStatusEnum.in_progress:
        raise HTTPException(status_code=400, detail="Session is not in progress")
    return await cancel_session(db, session)
