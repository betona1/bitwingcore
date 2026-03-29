"""사원 PC 관리 모델."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from bitwingcore.database import Base


class ManagedPC(Base):
    """사원 PC 관리 테이블."""

    __tablename__ = "managed_pcs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    hostname: Mapped[str] = mapped_column(String(200), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    os_type: Mapped[str] = mapped_column(
        Enum("windows", "linux", name="os_type"), nullable=False
    )
    employee_name: Mapped[str | None] = mapped_column(String(100))
    department: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(
        Enum("online", "offline", "maintenance", name="pc_status"),
        default="offline",
        index=True,
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime)
    system_info: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )
