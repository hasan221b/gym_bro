import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

# --- Load our app config (reads DATABASE_URL from .env) ---
from app.core.config import settings

# --- Import Base so Alembic knows about our schema ---
from app.db.database import Base

# --- Import ALL models so they register themselves on Base.metadata ---
# If you skip any model here, Alembic won't see it and won't generate its table.
import app.models  # noqa: F401  (the __init__.py imports all models)

# Alembic config object — gives access to alembic.ini values
config = context.config

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# This is what Alembic compares against your DB to find differences
target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# OFFLINE mode: generates SQL script without connecting to the DB.
# Useful for reviewing what will run before touching the real DB.
# Run with: alembic upgrade head --sql
# ---------------------------------------------------------------------------
def run_migrations_offline() -> None:
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# ONLINE mode: connects to the DB and runs migrations directly.
# Run with: alembic upgrade head
# ---------------------------------------------------------------------------
def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    # Create async engine using our DATABASE_URL (postgresql+asyncpg://...)
    connectable = create_async_engine(settings.DATABASE_URL)

    async with connectable.connect() as connection:
        # run_sync lets Alembic (which is sync) work through our async connection
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


# Entry point — Alembic calls this file, we decide online vs offline
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
