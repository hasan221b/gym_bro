from fastapi import APIRouter

from app.api.v1.endpoints import users, exercises, routines, sessions, progress, utils, agent

router = APIRouter(prefix="/api/v1")

router.include_router(users.router)
router.include_router(exercises.router)
router.include_router(routines.router)
router.include_router(sessions.router)
router.include_router(progress.router)
router.include_router(utils.router)
router.include_router(agent.router)
