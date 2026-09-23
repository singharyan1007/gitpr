from fastapi import APIRouter, Request

from app.infra.github_client import GitHubClient

router = APIRouter()


@router.get("/health")
async def health(request: Request):
    checks = {"database": "unknown", "redis": "unknown", "github": "unknown"}

    try:
        await request.app.state.repository.stats_for_repo("healthcheck", "healthcheck")
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "error"

    try:
        await request.app.state.redis_pool.ping()
        checks["redis"] = "ok"
    except Exception:
        checks["redis"] = "error"

    try:
        client = GitHubClient(request.app.state.http, request.app.state.settings)
        await client.get_rate_limit()
        checks["github"] = "ok"
    except Exception:
        checks["github"] = "error"

    return checks
