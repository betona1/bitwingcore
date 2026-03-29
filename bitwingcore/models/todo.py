"""할일 모델."""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from bitwingcore.database import Base


class Todo(Base):
    """할일 목록 테이블."""

    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(
        Enum("urgent", "high", "normal", "low", name="todo_priority"),
        default="normal",
    )
    status: Mapped[str] = mapped_column(
        Enum("pending", "in_progress", "completed", "cancelled", name="todo_status"),
        default="pending",
        index=True,
    )
    due_date: Mapped[date | None] = mapped_column(Date, index=True)
    assigned_manager: Mapped[str | None] = mapped_column(String(50), comment="담당 매니저")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )
