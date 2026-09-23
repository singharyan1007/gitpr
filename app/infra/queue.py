from arq import create_pool
from arq.connections import RedisSettings

from app.config import Settings


async def make_redis_pool(settings: Settings):
    return await create_pool(RedisSettings.from_dsn(settings.redis_url))


async def enqueue_review(pool, *, owner: str, repo: str, number: int, head_sha: str) -> None:
    # Job id keyed on the exact commit reviewed: GitHub's webhook retries land
    # on the same _job_id and arq dedupes them instead of double-enqueueing.
    job_id = f"review:{owner}:{repo}:{number}:{head_sha}"
    await pool.enqueue_job("review_pr", owner, repo, number, head_sha, _job_id=job_id)
