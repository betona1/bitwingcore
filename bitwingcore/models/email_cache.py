"""이메일 캐시 모델."""

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from bitwingcore.database import Base


class EmailCache(Base):
    """이메일 캐시 테이블."""

    __tablename__ = "email_cache"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email_provider: Mapped[str] = mapped_column(
        Enum("gmail", "outlook", "imap", name="email_provider"), nullable=False
    )
    message_id: Mapped[str | None] = mapped_column(String(200), unique=True)
    subject: Mapped[str | None] = mapped_column(String(500))
    sender: Mapped[str | None] = mapped_column(String(200))
    received_at: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    ai_summary: Mapped[str | None] = mapped_column(Text, comment="AI 요약")
    labels: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
