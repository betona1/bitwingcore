"""일정 관리 모듈."""

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bitwingcore.models.calendar import Calendar
from bitwingcore.modules.base import BaseModule, ModuleRegistry
from bitwingcore.utils.date_parser import parse_korean_date, parse_korean_time
from bitwingcore.utils.pagination import paginate


@ModuleRegistry.register("calendar_mod")
class CalendarModule(BaseModule):
    """일정(캘린더) CRUD 모듈."""

    display_name = "일정 관리"
    description = "일정 등록/조회/수정/삭제"
    supported_intents = [
        "schedule.create",
        "schedule.list",
        "schedule.update",
        "schedule.delete",
    ]

    async def execute(
        self,
        intent: str,
        params: dict[str, Any],
        db: AsyncSession,
    ) -> dict[str, Any]:
        """일정 모듈 실행."""
        action = intent.split(".")[-1]

        if action == "create":
            return await self._create(params, db)
        if action == "list":
            return await self._list(params, db)
        if action == "update":
            return await self._update(params, db)
        if action == "delete":
            return await self._delete(params, db)

        return {"message": "지원하지 않는 동작입니다."}

    async def _create(self, params: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
        """일정 생성."""
        raw_text = params.get("raw_text", "")
        title = params.get("title", raw_text)
        start_at = params.get("start_at")
        end_at = params.get("end_at")

        # 날짜/시간 파싱
        if not start_at:
            date_start, date_end = parse_korean_date(raw_text)
            time_parsed = parse_korean_time(raw_text)
            if time_parsed:
                start_at = time_parsed
                end_at = time_parsed.replace(hour=time_parsed.hour + 1)
            else:
                start_at = date_start.replace(hour=9)
                end_at = date_start.replace(hour=10)

        if not end_at:
            end_at = start_at.replace(hour=start_at.hour + 1) if isinstance(start_at, datetime) else start_at

        event = Calendar(
            title=title,
            description=params.get("description"),
            start_at=start_at,
            end_at=end_at,
            location=params.get("location"),
            reminder_minutes=params.get("reminder_minutes", 30),
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)

        return {
            "id": event.id,
            "title": event.title,
            "start_at": event.start_at,
            "end_at": event.end_at,
        }

    async def _list(self, params: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
        """일정 조회."""
        raw_text = params.get("raw_text", "오늘")
        date_start, date_end = parse_korean_date(raw_text)

        query = (
            select(Calendar)
            .where(Calendar.start_at >= date_start)
            .where(Calendar.start_at <= date_end)
            .where(Calendar.status == "active")
            .order_by(Calendar.start_at)
        )

        page = params.get("page", 1)
        items, meta = await paginate(db, query, page=page)

        return {
            "items": [
                {
                    "id": e.id,
                    "title": e.title,
                    "start_at": e.start_at,
                    "end_at": e.end_at,
                    "location": e.location,
                    "status": e.status,
                }
                for e in items
            ],
            "meta": meta,
        }

    async def _update(self, params: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
        """일정 수정."""
        event_id = params.get("id")
        if not event_id:
            return {"error": "일정 ID가 필요합니다."}

        result = await db.execute(select(Calendar).where(Calendar.id == event_id))
        event = result.scalar_one_or_none()
        if not event:
            return {"error": "일정을 찾을 수 없습니다."}

        for field in ("title", "description", "location", "start_at", "end_at", "reminder_minutes", "status"):
            if field in params:
                setattr(event, field, params[field])

        await db.commit()
        return {"id": event.id, "title": event.title, "message": "수정 완료"}

    async def _delete(self, params: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
        """일정 삭제 (상태 변경)."""
        event_id = params.get("id")
        if not event_id:
            return {"error": "일정 ID가 필요합니다."}

        result = await db.execute(select(Calendar).where(Calendar.id == event_id))
        event = result.scalar_one_or_none()
        if not event:
            return {"error": "일정을 찾을 수 없습니다."}

        event.status = "cancelled"
        await db.commit()
        return {"id": event.id, "message": "삭제 완료"}
