from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.infra.models import Review


class ReviewRepository:
    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def insert_if_new(
        self, *, owner: str, repo: str, pr_number: int, head_sha: str, findings_count: int, body: str
    ) -> bool:
        """Returns False (no error) if this exact commit was already reviewed."""
        async with self._session_factory() as session:
            session.add(
                Review(
                    owner=owner,
                    repo=repo,
                    pr_number=pr_number,
                    head_sha=head_sha,
                    findings_count=findings_count,
                    body=body,
                )
            )
            try:
                await session.commit()
                return True
            except IntegrityError:
                await session.rollback()
                return False

    async def list_for_repo(self, owner: str, repo: str, limit: int = 20) -> list[Review]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(Review)
                .where(Review.owner == owner, Review.repo == repo)
                .order_by(Review.created_at.desc())
                .limit(limit)
            )
            return list(result.scalars().all())

    async def stats_for_repo(self, owner: str, repo: str) -> dict:
        async with self._session_factory() as session:
            result = await session.execute(
                select(func.count(Review.id), func.avg(Review.findings_count)).where(
                    Review.owner == owner, Review.repo == repo
                )
            )
            count, avg_findings = result.one()
            return {"reviews": count or 0, "avg_findings": float(avg_findings or 0)}
