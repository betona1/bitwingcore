"""메모 관리 모듈."""

from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from bitwingcore.models.memo import Memo
from bitwingcore.modules.base import BaseModule, ModuleRegistry
from bitwingcore.utils.pagination import paginate


@ModuleRegistry.register("memo_mod")
class MemoModule(BaseModule):
    """메모 CRUD + 검색 모듈."""

    display_name = "메모 관리"
    description = "메모 저장/조회/검색/삭제"
    supported_intents = [
        "memo.create",
        "memo.list",
        "memo.search",
        "memo.delete",
    ]

    async def execute(
        self,
        intent: str,
        params: dict[str, Any],
        db: AsyncSession,
    ) -> dict[str, Any]:
        """메모 모듈 실행."""
        action = intent.split(".")[-1]

        if action == "create":
            return await self._create(params, db)
        if action == "list":
            return await self._list(params, db)
        if action == "search":
            return await self._search(params, db)
        if action == "delete":
            return await self._delete(params, db)

        return {"message": "지원하지 않는 동작입니다."}

    async def _create(self, params: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
        """메모 생성."""
        content = params.get("content", params.get("raw_text", ""))
        memo = Memo(
            title=params.get("title"),
            content=content,
            tags=params.get("tags"),
            category=params.get("category"),
        )
        db.add(memo)
        await db.commit()
        await db.refresh(memo)

        return {"id": memo.id, "title": memo.title, "content_preview": content[:100]}

    async def _list(self, params: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
        """메모 목록 조회."""
        query = select(Memo).order_by(Memo.created_at.desc())

        category = params.get("category")
        if category:
            query = query.where(Memo.category == category)

        page = params.get("page", 1)
        items, meta = await paginate(db, query, page=page)

        return {
            "items": [
                {
                    "id": m.id,
                    "title": m.title,
                    "content": (m.content or "")[:200],
                    "category": m.category,
                    "tags": m.tags,
                    "created_at": m.created_at,
                }
                for m in items
            ],
            "meta": meta,
        }

    async def _search(self, params: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
        """메모 검색."""
        keyword = params.get("keyword", params.get("raw_text", ""))
        if not keyword:
            return await self._list(params, db)

        query = (
            select(Memo)
            .where(
                or_(
                    Memo.title.contains(keyword),
                    Memo.content.contains(keyword),
                )
            )
            .order_by(Memo.created_at.desc())
        )

        page = params.get("page", 1)
        items, meta = await paginate(db, query, page=page)

        return {
            "items": [
                {
                    "id": m.id,
                    "title": m.title,
                    "content": (m.content or "")[:200],
                    "category": m.category,
                    "created_at": m.created_at,
                }
                for m in items
            ],
            "meta": meta,
            "keyword": keyword,
        }

    async def _delete(self, params: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
        """메모 삭제."""
        memo_id = params.get("id")
        if not memo_id:
            return {"error": "메모 ID가 필요합니다."}

        result = await db.execute(select(Memo).where(Memo.id == memo_id))
        memo = result.scalar_one_or_none()
        if not memo:
            return {"error": "메모를 찾을 수 없습니다."}

        await db.delete(memo)
        await db.commit()

        return {"id": memo_id, "message": "삭제 완료"}
