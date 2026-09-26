from datetime import datetime, timezone
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column,DeclarativeBase




class Base(DeclarativeBase):
    pass

class Review(Base):
    __tablename__="reviews"
    __table_args__=(
        UniqueConstraint("owner","repo","pr_number","head_sha",name="uq_review_commit",),
    )

    id:Mapped[int]=mapped_column(primary_key=True)
    owner:Mapped[str]
    repo:Mapped[str]
    pr_number:Mapped[int]
    head_sha:Mapped[str]
    findings_count:Mapped[int]
    body:Mapped[str]
    created_at:Mapped[datetime]=mapped_column(default=datetime.now(timezone.utc))