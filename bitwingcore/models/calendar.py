"""일정(캘린더) 모델."""

from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from bitwingcore.database import Base


class Calendar(Base):
    """일정/캘린더 테이블."""

    __tablename__ = "calendars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    start_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    end_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    location: Mapped[str | None] = mapped_column(String(500))
    reminder_minutes: Mapped[int] = mapped_column(Integer, default=30)
    status: Mapped[str] = mapped_column(
        Enum("active", "cancelled", "completed", name="calendar_status"),
        default="active",
    )
    google_event_id: Mapped[str | None] = mapped_column(
        String(200), index=True, comment="Google Calendar 이벤트 ID"
    )
    source: Mapped[str] = mapped_column(
        Enum("bitwing", "google", "manual", name="calendar_source"),
        default="bitwing",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )
