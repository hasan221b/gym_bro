import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.cruds.routine import routine_crud
from app.cruds.routine_exercise import routine_exercise_crud
from app.models.routines import Routine
from app.models.routine_exercise import RoutineExercise
from app.schemas.routine import RoutineCreate
from app.schemas.routine_exercise import RoutineExerciseCreate


async def create_routine(db: AsyncSession, user_id: int, data: RoutineCreate) -> Routine:
    return await routine_crud.create(db, {
        "user_id": user_id,
        "name": data.name,
        "description": data.description,
    })


async def add_exercise(
    db: AsyncSession,
    routine_id: uuid.UUID,
    data: RoutineExerciseCreate
) -> RoutineExercise:
    # Get current max order in this routine to place new exercise at the end
    result = await db.execute(
        select(func.max(RoutineExercise.order))
        .where(RoutineExercise.routine_id == routine_id)
    )
    max_order = result.scalar() or 0

    created = await routine_exercise_crud.create(db, {
        "routine_id": routine_id,
        "exercise_id": data.exercise_id,
        "order": max_order + 1,
        "planned_sets": data.planned_sets,
        "planned_reps": data.planned_reps,
        "planned_weight": data.planned_weight,
        "notes": data.notes,
    })
    return await routine_exercise_crud.get_with_exercise(db, created.id)


async def remove_exercise(db: AsyncSession, routine_exercise_id: uuid.UUID) -> None:
    obj = await routine_exercise_crud.get(db, routine_exercise_id)
    if obj:
        await routine_exercise_crud.delete(db, obj)


async def reorder_exercises(
    db: AsyncSession,
    routine_id: uuid.UUID,
    order_map: dict[uuid.UUID, int]   # {routine_exercise_id: new_order}
) -> list[RoutineExercise]:
    exercises = await routine_exercise_crud.get_by_routine(db, routine_id)
    for exercise in exercises:
        if exercise.id in order_map:
            await routine_exercise_crud.update(db, exercise, {"order": order_map[exercise.id]})
    return await routine_exercise_crud.get_by_routine(db, routine_id)
