from app.db.database import engine, Base
import app.models  # noqa: F401 — ensures all models are registered on Base.metadata


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
