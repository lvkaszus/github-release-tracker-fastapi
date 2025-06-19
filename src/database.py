from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

load_dotenv()

DATA_DIR = "data"
DB_FILENAME = "gh_rapi-db.sql"
DB_PATH = os.path.join(DATA_DIR, DB_FILENAME)

os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

engine = create_async_engine(DATABASE_URL)
Base = declarative_base()
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


redis_client = aioredis.from_url(os.getenv("REDIS_URI"))
FastAPICache.init(RedisBackend(redis_client), prefix="api-cache")


@asynccontextmanager
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

