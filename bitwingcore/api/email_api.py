"""이메일 API — 이메일 목록/요약."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bitwingcore.auth import verify_api_key
from bitwingcore.database import get_db
from bitwingcore.models.email_cache import EmailCache
from bitwingcore.utils.pagination import paginate
from bitwingcore.utils.response import error_response, success_response

router = APIRouter(prefix="/emails", tags=["emails"])


@router.get("")
async def list_emails(
    unread_only: bool = False,
    provider: str | None = None,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """이메일 목록 조회."""
    query = select(EmailCache).order_by(EmailCache.received_at.desc())

    if unread_only:
        query = query.where(EmailCache.is_read == False)  # noqa: E712
    if provider:
        query = query.where(EmailCache.email_provider == provider)

    items, meta = await paginate(db, query, page=page, size=size)

    return success_response(
        data={
            "items": [
                {
                    "id": e.id,
                    "subject": e.subject,
                    "sender": e.sender,
                    "received_at": str(e.received_at) if e.received_at else None,
                    "is_read": e.is_read,
                    "provider": e.email_provider,
                    "has_summary": bool(e.ai_summary),
                }
                for e in items
            ],
            "meta": meta,
        }
    )


@router.get("/{email_id}")
async def get_email(
    email_id: int,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """이메일 상세 조회."""
    result = await db.execute(select(EmailCache).where(EmailCache.id == email_id))
    email = result.scalar_one_or_none()
    if not email:
        error_response("이메일을 찾을 수 없습니다.", 404)

    # 읽음 처리
    if not email.is_read:
        email.is_read = True
        await db.commit()

    return success_response(
        data={
            "id": email.id,
            "subject": email.subject,
            "sender": email.sender,
            "received_at": str(email.received_at) if email.received_at else None,
            "is_read": email.is_read,
            "ai_summary": email.ai_summary,
            "labels": email.labels,
            "provider": email.email_provider,
            "message_id": email.message_id,
        }
    )


@router.get("/{email_id}/summary")
async def get_email_summary(
    email_id: int,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """이메일 AI 요약 조회."""
    result = await db.execute(select(EmailCache).where(EmailCache.id == email_id))
    email = result.scalar_one_or_none()
    if not email:
        error_response("이메일을 찾을 수 없습니다.", 404)

    return success_response(
        data={
            "id": email.id,
            "subject": email.subject,
            "ai_summary": email.ai_summary or "요약이 아직 생성되지 않았습니다.",
        }
    )
