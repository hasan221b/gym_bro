from fastapi import APIRouter

from app.api.v1.endpoints import chat_agent, review_agent, create_agent, users, exercises, routines, sessions, progress, utils

router = APIRouter(prefix="/api/v1")

router.include_router(users.router)
router.include_router(exercises.router)
router.include_router(routines.router)
router.include_router(sessions.router)
router.include_router(progress.router)
router.include_router(utils.router)
router.include_router(chat_agent.router)
router.include_router(review_agent.router)
router.include_router(create_agent.router)
