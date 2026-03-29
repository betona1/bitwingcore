"""파일 관리 모델."""

from datetime import datetime

from sqlalchemy import JSON, BigInteger, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from bitwingcore.database import Base


class ManagedFile(Base):
    """파일 관리 테이블."""

    __tablename__ = "managed_files"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    filepath: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size: Mapped[int | None] = mapped_column(BigInteger)
    mime_type: Mapped[str | None] = mapped_column(String(100))
    category: Mapped[str | None] = mapped_column(String(100), index=True)
    access_level: Mapped[str] = mapped_column(
        Enum("public", "manager", "private", name="access_level"),
        default="public",
        index=True,
    )
    allowed_managers: Mapped[dict | None] = mapped_column(JSON)
    uploaded_by: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
