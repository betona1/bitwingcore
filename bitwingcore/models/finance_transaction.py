"""가계부 거래 모델."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from bitwingcore.database import Base


class FinanceTransaction(Base):
    """가계부 거래내역 테이블."""

    __tablename__ = "finance_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(
        Enum("income", "expense", name="finance_type"), nullable=False, index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True, comment="식비/교통/쇼핑 등")
    subcategory: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(500))
    payment_method: Mapped[str | None] = mapped_column(String(100), comment="현금/카드/이체 등")
    bank_name: Mapped[str | None] = mapped_column(String(100))
    card_name: Mapped[str | None] = mapped_column(String(100))
    merchant: Mapped[str | None] = mapped_column(String(200), comment="가맹점")
    receipt_image_path: Mapped[str | None] = mapped_column(String(500))
    source: Mapped[str] = mapped_column(
        Enum("manual", "bank_api", "ocr", "crawling", name="finance_source"),
        default="manual",
    )
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
