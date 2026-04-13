from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db.init_db import create_tables
from app.api.v1.router import router

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router)

# Serve frontend — accessible at http://localhost:8000/app/
app.mount("/ui", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
