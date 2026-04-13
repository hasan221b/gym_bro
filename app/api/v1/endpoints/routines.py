import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.cruds.routine import routine_crud
from app.cruds.routine_exercise import routine_exercise_crud
from app.schemas.routine import RoutineCreate, RoutineUpdate, RoutineResponse, RoutineDetailResponse
from app.schemas.routine_exercise import RoutineExerciseCreate, RoutineExerciseUpdate, RoutineExerciseResponse
from app.services.routine_service import create_routine, add_exercise, remove_exercise, reorder_exercises

router = APIRouter(prefix="/routines", tags=["Routines"])


@router.get("/user/{user_id}", response_model=list[RoutineResponse])
async def get_user_routines(user_id: int, db: AsyncSession = Depends(get_db)):
    return await routine_crud.get_by_user(db, user_id)


@router.get("/{routine_id}", response_model=RoutineDetailResponse)
async def get_routine(routine_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    routine = await routine_crud.get_with_exercises(db, routine_id)
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    return routine


@router.post("", status_code=201, response_model=RoutineResponse)
async def create_routine_endpoint(
    user_id: int,
    data: RoutineCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_routine(db, user_id, data)


@router.patch("/{routine_id}", response_model=RoutineResponse)
async def update_routine(
    routine_id: uuid.UUID,
    data: RoutineUpdate,
    db: AsyncSession = Depends(get_db)
):
    routine = await routine_crud.get(db, routine_id)
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    return await routine_crud.update(db, routine, data.model_dump(exclude_unset=True))


@router.delete("/{routine_id}", status_code=204)
async def delete_routine(routine_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    routine = await routine_crud.get(db, routine_id)
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    await routine_crud.delete(db, routine)


@router.post("/{routine_id}/exercises", status_code=201, response_model=RoutineExerciseResponse)
async def add_exercise_to_routine(
    routine_id: uuid.UUID,
    data: RoutineExerciseCreate,
    db: AsyncSession = Depends(get_db)
):
    routine = await routine_crud.get(db, routine_id)
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    return await add_exercise(db, routine_id, data)


@router.patch("/{routine_id}/exercises/{routine_exercise_id}", response_model=RoutineExerciseResponse)
async def update_routine_exercise(
    routine_id: uuid.UUID,
    routine_exercise_id: uuid.UUID,
    data: RoutineExerciseUpdate,
    db: AsyncSession = Depends(get_db)
):
    re = await routine_exercise_crud.get(db, routine_exercise_id)
    if not re or re.routine_id != routine_id:
        raise HTTPException(status_code=404, detail="Routine exercise not found")
    return await routine_exercise_crud.update(db, re, data.model_dump(exclude_unset=True))


@router.delete("/{routine_id}/exercises/{routine_exercise_id}", status_code=204)
async def remove_exercise_from_routine(
    routine_id: uuid.UUID,
    routine_exercise_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    re = await routine_exercise_crud.get(db, routine_exercise_id)
    if not re or re.routine_id != routine_id:
        raise HTTPException(status_code=404, detail="Routine exercise not found")
    await remove_exercise(db, routine_exercise_id)


@router.patch("/{routine_id}/reorder", response_model=list[RoutineExerciseResponse])
async def reorder_routine_exercises(
    routine_id: uuid.UUID,
    order_map: dict[uuid.UUID, int],
    db: AsyncSession = Depends(get_db)
):
    routine = await routine_crud.get(db, routine_id)
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    return await reorder_exercises(db, routine_id, order_map)
