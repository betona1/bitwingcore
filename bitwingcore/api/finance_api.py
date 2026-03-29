"""가계부 API — 수입/지출 CRUD + 요약."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bitwingcore.api.schemas import FinanceCreate, FinanceUpdate
from bitwingcore.auth import verify_api_key
from bitwingcore.database import get_db
from bitwingcore.models.finance_transaction import FinanceTransaction
from bitwingcore.utils.date_parser import parse_korean_date
from bitwingcore.utils.pagination import paginate
from bitwingcore.utils.response import error_response, success_response

router = APIRouter(prefix="/finance", tags=["finance"])


@router.get("/transactions")
async def list_transactions(
    date_range: str = "이번달",
    type: str | None = None,
    category: str | None = None,
    page: int = 1,
    size: int = 50,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """거래 내역 조회."""
    date_start, date_end = parse_korean_date(date_range)

    query = (
        select(FinanceTransaction)
        .where(FinanceTransaction.transaction_date >= date_start.date())
        .where(FinanceTransaction.transaction_date <= date_end.date())
        .order_by(FinanceTransaction.transaction_date.desc())
    )

    if type:
        query = query.where(FinanceTransaction.type == type)
    if category:
        query = query.where(FinanceTransaction.category == category)

    items, meta = await paginate(db, query, page=page, size=size)

    return success_response(
        data={
            "items": [
                {
                    "id": t.id,
                    "type": t.type,
                    "amount": float(t.amount),
                    "category": t.category,
                    "subcategory": t.subcategory,
                    "description": t.description,
                    "payment_method": t.payment_method,
                    "merchant": t.merchant,
                    "transaction_date": str(t.transaction_date),
                }
                for t in items
            ],
            "meta": meta,
        }
    )


@router.get("/summary")
async def get_summary(
    date_range: str = "이번달",
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """가계부 요약 통계."""
    date_start, date_end = parse_korean_date(date_range)
    base_filter = [
        FinanceTransaction.transaction_date >= date_start.date(),
        FinanceTransaction.transaction_date <= date_end.date(),
    ]

    # 수입/지출 합계
    income_result = await db.execute(
        select(func.coalesce(func.sum(FinanceTransaction.amount), 0))
        .where(*base_filter, FinanceTransaction.type == "income")
    )
    total_income = float(income_result.scalar() or 0)

    expense_result = await db.execute(
        select(func.coalesce(func.sum(FinanceTransaction.amount), 0))
        .where(*base_filter, FinanceTransaction.type == "expense")
    )
    total_expense = float(expense_result.scalar() or 0)

    # 카테고리별
    cat_result = await db.execute(
        select(FinanceTransaction.category, func.sum(FinanceTransaction.amount))
        .where(*base_filter, FinanceTransaction.type == "expense")
        .group_by(FinanceTransaction.category)
        .order_by(func.sum(FinanceTransaction.amount).desc())
    )
    categories = {row[0]: float(row[1]) for row in cat_result.all()}

    return success_response(
        data={
            "period": date_range,
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": total_income - total_expense,
            "expense_by_category": categories,
        }
    )


@router.get("/transactions/{tx_id}")
async def get_transaction(
    tx_id: int,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """거래 상세 조회."""
    result = await db.execute(select(FinanceTransaction).where(FinanceTransaction.id == tx_id))
    tx = result.scalar_one_or_none()
    if not tx:
        error_response("거래를 찾을 수 없습니다.", 404)

    return success_response(
        data={
            "id": tx.id,
            "type": tx.type,
            "amount": float(tx.amount),
            "category": tx.category,
            "subcategory": tx.subcategory,
            "description": tx.description,
            "payment_method": tx.payment_method,
            "bank_name": tx.bank_name,
            "card_name": tx.card_name,
            "merchant": tx.merchant,
            "receipt_image_path": tx.receipt_image_path,
            "source": tx.source,
            "transaction_date": str(tx.transaction_date),
        }
    )


@router.post("/transactions")
async def create_transaction(
    req: FinanceCreate,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """거래 기록 추가."""
    tx = FinanceTransaction(
        type=req.type,
        amount=req.amount,
        category=req.category,
        subcategory=req.subcategory,
        description=req.description,
        payment_method=req.payment_method,
        merchant=req.merchant,
        transaction_date=req.transaction_date,
    )
    db.add(tx)
    await db.commit()
    await db.refresh(tx)

    type_display = "수입" if req.type == "income" else "지출"
    return success_response(
        data={"id": tx.id, "type": req.type, "amount": float(tx.amount)},
        message=f"{type_display} {float(tx.amount):,.0f}원을 기록했습니다.",
    )


@router.put("/transactions/{tx_id}")
async def update_transaction(
    tx_id: int,
    req: FinanceUpdate,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """거래 수정."""
    result = await db.execute(select(FinanceTransaction).where(FinanceTransaction.id == tx_id))
    tx = result.scalar_one_or_none()
    if not tx:
        error_response("거래를 찾을 수 없습니다.", 404)

    update_data = req.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tx, field, value)

    await db.commit()
    return success_response(message="거래를 수정했습니다.")


@router.delete("/transactions/{tx_id}")
async def delete_transaction(
    tx_id: int,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """거래 삭제."""
    result = await db.execute(select(FinanceTransaction).where(FinanceTransaction.id == tx_id))
    tx = result.scalar_one_or_none()
    if not tx:
        error_response("거래를 찾을 수 없습니다.", 404)

    await db.delete(tx)
    await db.commit()
    return success_response(message="거래를 삭제했습니다.")
