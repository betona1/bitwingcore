"""시스템 로그 모델."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from bitwingcore.database import Base


class SystemLog(Base):
    """시스템 로그 테이블."""

    __tablename__ = "system_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    level: Mapped[str] = mapped_column(
        Enum("info", "warning", "error", "critical", name="log_level"),
        default="info",
        index=True,
    )
    module: Mapped[str | None] = mapped_column(String(50))
    manager: Mapped[str | None] = mapped_column(String(50))
    message: Mapped[str | None] = mapped_column(Text)
    details: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)
