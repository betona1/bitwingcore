"""외부 연동 설정 모델."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from bitwingcore.database import Base


class Integration(Base):
    """외부 서비스 연동 테이블."""

    __tablename__ = "integrations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    service: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True, comment="google_calendar, gmail, bank 등"
    )
    status: Mapped[str] = mapped_column(
        Enum("connected", "disconnected", "error", name="integration_status"),
        default="disconnected",
    )
    config: Mapped[dict | None] = mapped_column(JSON, comment="연동 설정 (OAuth 토큰 등, 암호화)")
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )
