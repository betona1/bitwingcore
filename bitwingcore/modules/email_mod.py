"""이메일 관리 모듈."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bitwingcore.models.email_cache import EmailCache
from bitwingcore.modules.base import BaseModule, ModuleRegistry
from bitwingcore.utils.pagination import paginate


@ModuleRegistry.register("email_mod")
class EmailModule(BaseModule):
    """이메일 조회/요약 모듈."""

    display_name = "이메일 관리"
    description = "이메일 목록 조회 및 AI 요약"
    supported_intents = [
        "email.list",
        "email.summary",
    ]

    async def execute(
        self,
        intent: str,
        params: dict[str, Any],
        db: AsyncSession,
    ) -> dict[str, Any]:
        """이메일 모듈 실행."""
        action = intent.split(".")[-1]

        if action == "list":
            return await self._list(params, db)
        if action == "summary":
            return await self._summary(params, db)

        return {"message": "지원하지 않는 동작입니다."}

    async def _list(self, params: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
        """이메일 목록 조회."""
        query = select(EmailCache).order_by(EmailCache.received_at.desc())

        # 읽지 않은 메일 필터
        unread_only = params.get("unread_only", False)
        if unread_only:
            query = query.where(EmailCache.is_read == False)  # noqa: E712

        page = params.get("page", 1)
        items, meta = await paginate(db, query, page=page, size=20)

        return {
            "items": [
                {
                    "id": e.id,
                    "subject": e.subject,
                    "sender": e.sender,
                    "received_at": e.received_at,
                    "is_read": e.is_read,
                    "provider": e.email_provider,
                }
                for e in items
            ],
            "meta": meta,
        }

    async def _summary(self, params: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
        """이메일 요약 (캐시된 AI 요약 반환)."""
        email_id = params.get("id")

        if email_id:
            result = await db.execute(select(EmailCache).where(EmailCache.id == email_id))
            email = result.scalar_one_or_none()
            if not email:
                return {"error": "이메일을 찾을 수 없습니다."}
            return {
                "id": email.id,
                "subject": email.subject,
                "sender": email.sender,
                "ai_summary": email.ai_summary or "요약이 아직 생성되지 않았습니다.",
            }

        # 최근 읽지 않은 메일 요약
        result = await db.execute(
            select(EmailCache)
            .where(EmailCache.is_read == False)  # noqa: E712
            .order_by(EmailCache.received_at.desc())
            .limit(5)
        )
        emails = list(result.scalars().all())

        return {
            "items": [
                {
                    "id": e.id,
                    "subject": e.subject,
                    "sender": e.sender,
                    "ai_summary": e.ai_summary or "요약 없음",
                }
                for e in emails
            ],
            "total_unread": len(emails),
        }
