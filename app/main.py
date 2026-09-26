from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI


from app.config import get_settings
from app.api import webhook
from app.infra.db import init_db, make_engine, make_session_factory
from app.infra.repositories import ReviewRepository



@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.settings = settings
    app.state.http = httpx.AsyncClient(timeout=15,follow_redirects=True)

    #initialize the DB engine
    engine = make_engine(app.state.settings)
    await init_db(engine)
    app.state.repository = ReviewRepository(make_session_factory(engine))

    yield

    await app.state.http.aclose()


app = FastAPI(title="github-review-bot", lifespan=lifespan)
app.include_router(webhook.router, prefix="/api", tags=["webhook"])
