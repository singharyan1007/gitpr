from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.api import health, history, webhook
from app.config import get_settings
from app.infra.db import init_db, make_engine, make_session_factory
from app.infra.queue import make_redis_pool
from app.infra.repositories import ReviewRepository
from app.logging_config import configure_logging

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.settings = settings
    app.state.http = httpx.AsyncClient(timeout=15)
    app.state.redis_pool = await make_redis_pool(settings)

    engine = make_engine(settings)
    await init_db(engine)
    app.state.repository = ReviewRepository(make_session_factory(engine))

    yield

    await app.state.http.aclose()
    await app.state.redis_pool.close()


app = FastAPI(title="github-review-bot", lifespan=lifespan)
app.include_router(webhook.router)
app.include_router(history.router)
app.include_router(health.router)
