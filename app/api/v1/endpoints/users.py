from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.cruds.user import user_crud
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", status_code=201, response_model=UserResponse)
async def upsert_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    await user_crud.upsert(db, data)
    return await user_crud.get(db, data.id)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
