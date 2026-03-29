"""가계부 관리 모듈."""

from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bitwingcore.models.finance_transaction import FinanceTransaction
from bitwingcore.modules.base import BaseModule, ModuleRegistry
from bitwingcore.utils.date_parser import parse_korean_amount, parse_korean_date
from bitwingcore.utils.pagination import paginate


@ModuleRegistry.register("finance_mod")
class FinanceModule(BaseModule):
    """가계부 CRUD + 요약 모듈."""

    display_name = "가계부"
    description = "수입/지출 기록, 조회, 통계 요약"
    supported_intents = [
        "finance.add",
        "finance.list",
        "finance.summary",
    ]

    async def execute(
        self,
        intent: str,
        params: dict[str, Any],
        db: AsyncSession,
    ) -> dict[str, Any]:
        """가계부 모듈 실행."""
        action = intent.split(".")[-1]

        if action == "add":
            return await self._add(params, db)
        if action == "list":
            return await self._list(params, db)
        if action == "summary":
            return await self._summary(params, db)

        return {"message": "지원하지 않는 동작입니다."}

    async def _add(self, params: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
        """거래 기록 추가."""
        raw_text = params.get("raw_text", "")

        # 금액 파싱
        amount = params.get("amount")
        if not amount and raw_text:
            parsed = parse_korean_amount(raw_text)
            if parsed:
                amount = parsed

        if not amount:
            return {"error": "금액을 파악할 수 없습니다."}

        # 날짜 파싱
        transaction_date = params.get("transaction_date")
        if not transaction_date:
            date_start, _ = parse_korean_date(raw_text)
            transaction_date = date_start.date()

        tx_type = params.get("type", "expense")
        type_display = "수입" if tx_type == "income" else "지출"

        tx = FinanceTransaction(
            type=tx_type,
            amount=Decimal(str(amount)),
            category=params.get("category", "기타"),
            subcategory=params.get("subcategory"),
            description=params.get("description", raw_text[:200] if raw_text else None),
            payment_method=params.get("payment_method"),
            merchant=params.get("merchant"),
            transaction_date=transaction_date,
        )
        db.add(tx)
        await db.commit()
        await db.refresh(tx)

        return {
            "id": tx.id,
            "type": tx_type,
            "type_display": type_display,
            "amount": float(tx.amount),
            "category": tx.category,
            "transaction_date": tx.transaction_date,
        }

    async def _list(self, params: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
        """거래 내역 조회."""
        raw_text = params.get("raw_text", "이번달")
        date_start, date_end = parse_korean_date(raw_text)

        query = (
            select(FinanceTransaction)
            .where(FinanceTransaction.transaction_date >= date_start.date())
            .where(FinanceTransaction.transaction_date <= date_end.date())
            .order_by(FinanceTransaction.transaction_date.desc())
        )

        tx_type = params.get("type")
        if tx_type:
            query = query.where(FinanceTransaction.type == tx_type)

        page = params.get("page", 1)
        items, meta = await paginate(db, query, page=page)

        return {
            "items": [
                {
                    "id": t.id,
                    "type": t.type,
                    "amount": float(t.amount),
                    "category": t.category,
                    "description": t.description,
                    "merchant": t.merchant,
                    "transaction_date": t.transaction_date,
                }
                for t in items
            ],
            "meta": meta,
        }

    async def _summary(self, params: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
        """가계부 요약 통계."""
        raw_text = params.get("raw_text", "이번달")
        date_start, date_end = parse_korean_date(raw_text)

        base_filter = [
            FinanceTransaction.transaction_date >= date_start.date(),
            FinanceTransaction.transaction_date <= date_end.date(),
        ]

        # 총 수입
        income_result = await db.execute(
            select(func.coalesce(func.sum(FinanceTransaction.amount), 0))
            .where(*base_filter)
            .where(FinanceTransaction.type == "income")
        )
        total_income = float(income_result.scalar() or 0)

        # 총 지출
        expense_result = await db.execute(
            select(func.coalesce(func.sum(FinanceTransaction.amount), 0))
            .where(*base_filter)
            .where(FinanceTransaction.type == "expense")
        )
        total_expense = float(expense_result.scalar() or 0)

        # 카테고리별 지출
        cat_result = await db.execute(
            select(FinanceTransaction.category, func.sum(FinanceTransaction.amount))
            .where(*base_filter)
            .where(FinanceTransaction.type == "expense")
            .group_by(FinanceTransaction.category)
            .order_by(func.sum(FinanceTransaction.amount).desc())
        )
        expense_by_category = {row[0]: float(row[1]) for row in cat_result.all()}

        return {
            "period": raw_text,
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": total_income - total_expense,
            "expense_by_category": expense_by_category,
        }
