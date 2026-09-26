# Following the clean architecture, its the repository layer to hide the db details, and perform the db operations.

from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, select
from app.infra.models import Review

class ReviewRepository:
    def __init__(self,session_factory):
        self._session_factory = session_factory

    async def insert_if_new(self,
                            *,
                            owner:str,
                            repo:str,
                            pr_number:int,
                            head_sha:str,
                            findings_count:int,
                            body:str) -> bool:
            """
            Checks if the PR is new, or is it an old one, based on the unique constraints I have given. If True then new PR else old PR.
            Try to save this review. If the database accepts it, return True. If the database says this exact review already exists, undo the failed transaction and return False.
            """
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