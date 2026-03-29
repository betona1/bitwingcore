"""은행 계좌 모델."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import JSON, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from bitwingcore.database import Base


class BankAccount(Base):
    """은행 계좌 테이블."""

    __tablename__ = "bank_accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bank_name: Mapped[str] = mapped_column(String(100), nullable=False)
    account_number_masked: Mapped[str | None] = mapped_column(String(50), comment="마스킹된 계좌번호")
    account_type: Mapped[str | None] = mapped_column(String(50))
    balance: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime)
    config: Mapped[dict | None] = mapped_column(JSON, comment="연동 설정 (암호화)")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
