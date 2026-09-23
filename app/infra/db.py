from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from app.config import Settings
from app.infra.models import Base


def make_engine(settings: Settings) -> AsyncEngine:
    return create_async_engine(settings.database_url)


def make_session_factory(engine: AsyncEngine):
    return async_sessionmaker(engine, expire_on_commit=False)


async def init_db(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
