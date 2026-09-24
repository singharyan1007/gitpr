from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI


from app.config import get_settings
from app.api import webhook



@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.settings = settings
    app.state.http = httpx.AsyncClient(timeout=15)

    yield

    await app.state.http.aclose()


app = FastAPI(title="github-review-bot", lifespan=lifespan)
app.include_router(webhook.router, prefix="/api", tags=["webhook"])
