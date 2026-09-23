import time

import httpx
from arq.connections import RedisSettings

from app.config import get_settings
from app.domain.checks import format_findings, run_all_checks
from app.infra.cache import Cache
from app.infra.db import init_db, make_engine, make_session_factory
from app.infra.github_client import GitHubClient, RateLimited
from app.infra.repositories import ReviewRepository


async def review_pr(ctx, owner: str, repo: str, number: int, head_sha: str) -> str:
    settings = ctx["settings"]
    http: httpx.AsyncClient = ctx["http"]
    cache: Cache = ctx["cache"]
    repository: ReviewRepository = ctx["repository"]

    github = GitHubClient(http, settings, cache)

    try:
        diff = await github.get_pr_diff(owner, repo, number)
    except RateLimited as exc:
        delay = max((exc.reset_at or 0) - int(time.time()), 30) if exc.reset_at else 60
        await ctx["redis"].enqueue_job(
            "review_pr", owner, repo, number, head_sha, _defer_by=delay
        )
        return f"requeued: rate limited, retrying in {delay}s"

    findings = run_all_checks(diff)
    body = format_findings(findings)
    await github.post_review_comment(owner, repo, number, body)

    inserted = await repository.insert_if_new(
        owner=owner,
        repo=repo,
        pr_number=number,
        head_sha=head_sha,
        findings_count=len(findings),
        body=body,
    )
    return "ok" if inserted else "duplicate: already reviewed this commit"


async def startup(ctx) -> None:
    settings = get_settings()
    ctx["settings"] = settings
    ctx["http"] = httpx.AsyncClient(timeout=15)
    # arq injects ctx["redis"] automatically (an ArqRedis instance, which is
    # also a full redis client) — reuse it for caching instead of opening a
    # second connection.
    ctx["cache"] = Cache(ctx["redis"])

    engine = make_engine(settings)
    await init_db(engine)
    ctx["repository"] = ReviewRepository(make_session_factory(engine))


async def shutdown(ctx) -> None:
    await ctx["http"].aclose()


_settings = get_settings()


class WorkerSettings:
    functions = [review_pr]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(_settings.redis_url)
    max_tries = 5  # bounded retries; after this arq marks the job failed rather than looping forever
