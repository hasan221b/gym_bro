"""
Exercise catalogue loader for the create_agent.

load_exercise_catalogue_sync() is called at module import time by prompt.py.
It runs the async DB query in a dedicated background thread (own event loop)
so it works without psycopg2 and without a running asyncio loop.

Result is cached for the lifetime of the process.
"""

import asyncio
import concurrent.futures
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings
from app.models.exercises import Exercise

log = logging.getLogger(__name__)
_cache: str | None = None


# ── Async fetch — uses a private engine so the app's shared pool is untouched ──
async def _fetch_exercises() -> str:
    # Create a fresh engine + session factory local to this background thread's
    # event loop.  Never touch the app's shared engine here.
    _engine = create_async_engine(settings.DATABASE_URL)
    _Session = async_sessionmaker(_engine, expire_on_commit=False)

    stmt = (
        select(
            Exercise.name,
            Exercise.primary_muscles,
            Exercise.equipment,
        )
        .where(Exercise.is_custom == False)  # noqa: E712
        .order_by(Exercise.name)
    )

    try:
        async with _Session() as session:
            rows = (await session.execute(stmt)).mappings().all()
    finally:
        await _engine.dispose()

    def _muscles(lst) -> str:
        if not lst:
            return "—"
        return ", ".join(m.value if hasattr(m, "value") else str(m) for m in lst)

    def _equip(v) -> str:
        if v is None:
            return "—"
        return v.value if hasattr(v, "value") else str(v)

    lines = []
    for row in rows:
        lines.append(
            f"- {row['name']} | {_muscles(row['primary_muscles'])} | {_equip(row['equipment'])}"
        )

    return "\n".join(lines) if lines else "No exercises found in the library."


# ── Sync wrapper — runs async in its own thread + event loop ──────
def load_exercise_catalogue_sync() -> str:
    """
    Load the exercise catalogue synchronously.

    Spins up a private event loop in a ThreadPoolExecutor so it can be
    called at module import time without needing psycopg2 or an existing loop.
    """
    global _cache
    if _cache is not None:
        return _cache

    def _worker() -> str:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(_fetch_exercises())
        finally:
            loop.close()

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            _cache = pool.submit(_worker).result(timeout=30)
        log.info("Exercise catalogue loaded (%d chars)", len(_cache))
    except Exception as exc:
        log.error("Failed to load exercise catalogue: %s", exc)
        _cache = ""

    return _cache


def invalidate_cache() -> None:
    """Force a fresh DB load on the next call."""
    global _cache
    _cache = None
