import redis.asyncio as redis
from app.core.config import settings

# One shared async client for the whole app.
# Redis connections are cheap to reuse — no need for a pool like SQLAlchemy.
cache = redis.from_url(settings.REDIS_URL, decode_responses=True)
