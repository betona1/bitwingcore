"""대화 히스토리 모델."""

from datetime import datetime

from sqlalchemy import DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from bitwingcore.database import Base


class Conversation(Base):
    """대화 히스토리 테이블."""

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role: Mapped[str] = mapped_column(
        Enum("user", "assistant", "manager", name="conv_role"), nullable=False
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    intent: Mapped[str | None] = mapped_column(String(100))
    module: Mapped[str | None] = mapped_column(String(50))
    manager: Mapped[str | None] = mapped_column(String(50), index=True)
    client: Mapped[str] = mapped_column(
        Enum("mobile", "desktop", "web", name="client_type"), default="desktop"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)
