"""메모 API — Memo CRUD + 검색."""

from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from bitwingcore.api.schemas import MemoCreate, MemoUpdate
from bitwingcore.auth import verify_api_key
from bitwingcore.database import get_db
from bitwingcore.models.memo import Memo
from bitwingcore.utils.pagination import paginate
from bitwingcore.utils.response import error_response, success_response

router = APIRouter(prefix="/memos", tags=["memos"])


@router.get("")
async def list_memos(
    category: str | None = None,
    page: int = 1,
    size: int = 50,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """메모 목록 조회."""
    query = select(Memo).order_by(Memo.created_at.desc())

    if category:
        query = query.where(Memo.category == category)

    items, meta = await paginate(db, query, page=page, size=size)

    return success_response(
        data={
            "items": [
                {
                    "id": m.id,
                    "title": m.title,
                    "content": (m.content or "")[:200],
                    "category": m.category,
                    "tags": m.tags,
                    "created_at": str(m.created_at),
                }
                for m in items
            ],
            "meta": meta,
        }
    )


@router.get("/search")
async def search_memos(
    q: str,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """메모 검색."""
    query = (
        select(Memo)
        .where(or_(Memo.title.contains(q), Memo.content.contains(q)))
        .order_by(Memo.created_at.desc())
    )
    items, meta = await paginate(db, query, page=page, size=size)

    return success_response(
        data={
            "items": [
                {
                    "id": m.id,
                    "title": m.title,
                    "content": (m.content or "")[:200],
                    "category": m.category,
                    "created_at": str(m.created_at),
                }
                for m in items
            ],
            "meta": meta,
            "keyword": q,
        }
    )


@router.get("/{memo_id}")
async def get_memo(
    memo_id: int,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """메모 상세 조회."""
    result = await db.execute(select(Memo).where(Memo.id == memo_id))
    memo = result.scalar_one_or_none()
    if not memo:
        error_response("메모를 찾을 수 없습니다.", 404)

    return success_response(
        data={
            "id": memo.id,
            "title": memo.title,
            "content": memo.content,
            "category": memo.category,
            "tags": memo.tags,
            "created_at": str(memo.created_at),
            "updated_at": str(memo.updated_at),
        }
    )


@router.post("")
async def create_memo(
    req: MemoCreate,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """메모 생성."""
    memo = Memo(
        title=req.title,
        content=req.content,
        tags=req.tags,
        category=req.category,
    )
    db.add(memo)
    await db.commit()
    await db.refresh(memo)

    return success_response(
        data={"id": memo.id, "title": memo.title},
        message="메모를 저장했습니다.",
    )


@router.put("/{memo_id}")
async def update_memo(
    memo_id: int,
    req: MemoUpdate,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """메모 수정."""
    result = await db.execute(select(Memo).where(Memo.id == memo_id))
    memo = result.scalar_one_or_none()
    if not memo:
        error_response("메모를 찾을 수 없습니다.", 404)

    update_data = req.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(memo, field, value)

    await db.commit()
    return success_response(message="메모를 수정했습니다.")


@router.delete("/{memo_id}")
async def delete_memo(
    memo_id: int,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """메모 삭제."""
    result = await db.execute(select(Memo).where(Memo.id == memo_id))
    memo = result.scalar_one_or_none()
    if not memo:
        error_response("메모를 찾을 수 없습니다.", 404)

    await db.delete(memo)
    await db.commit()
    return success_response(message="메모를 삭제했습니다.")
