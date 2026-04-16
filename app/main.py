import asyncio
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# asyncpg is incompatible with Windows ProactorEventLoop (default on Python 3.8+)
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.db.init_db import create_tables
from app.api.v1.router import router
from app.core.cache import cache

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    try:
        await cache.ping()
        print("✅ Redis connected")
    except Exception as e:
        print("⚠️  Redis not connected — caching disabled")
        print(f"   Error: {e}")
    yield
    await cache.aclose()


app = FastAPI(lifespan=lifespan)

app.include_router(router)

# Serve frontend — accessible at http://localhost:8000/app/
app.mount("/ui", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
