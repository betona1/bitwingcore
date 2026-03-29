"""메모 모델."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from bitwingcore.database import Base


class Memo(Base):
    """메모 테이블."""

    __tablename__ = "memos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str | None] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[dict | None] = mapped_column(JSON)
    category: Mapped[str | None] = mapped_column(String(100), index=True)
    source: Mapped[str] = mapped_column(
        Enum("bitwing", "google_keep", "notion", "manual", name="memo_source"),
        default="bitwing",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )
