"""AI 매니저 모델."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from bitwingcore.database import Base


class Manager(Base):
    """AI 매니저 테이블."""

    __tablename__ = "managers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, comment="코드명")
    display_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="표시명")
    role: Mapped[str | None] = mapped_column(Text, comment="역할 설명")
    status: Mapped[str] = mapped_column(
        Enum("active", "busy", "idle", "disabled", name="manager_status"),
        default="idle",
    )
    modules: Mapped[dict | None] = mapped_column(JSON, comment="담당 모듈 목록")
    config: Mapped[dict | None] = mapped_column(JSON, comment="매니저 설정")
    total_tasks: Mapped[int] = mapped_column(Integer, default=0)
    last_active_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
