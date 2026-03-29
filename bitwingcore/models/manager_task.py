"""매니저 작업 히스토리 모델."""

from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from bitwingcore.database import Base


class ManagerTask(Base):
    """매니저 작업 히스토리 테이블."""

    __tablename__ = "manager_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    manager: Mapped[str] = mapped_column(String(50), nullable=False, index=True, comment="매니저 코드명")
    intent: Mapped[str | None] = mapped_column(String(100), comment="의도 분류")
    request: Mapped[str | None] = mapped_column(Text, comment="사용자 요청 원문")
    response: Mapped[str | None] = mapped_column(Text, comment="매니저 응답")
    status: Mapped[str] = mapped_column(
        Enum("pending", "processing", "completed", "failed", name="task_status"),
        default="pending",
        index=True,
    )
    duration_ms: Mapped[int | None] = mapped_column(Integer, comment="처리 소요시간(ms)")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
