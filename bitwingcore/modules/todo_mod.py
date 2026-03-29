"""할일 관리 모듈."""

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bitwingcore.models.todo import Todo
from bitwingcore.modules.base import BaseModule, ModuleRegistry
from bitwingcore.utils.date_parser import parse_korean_date
from bitwingcore.utils.pagination import paginate


@ModuleRegistry.register("todo_mod")
class TodoModule(BaseModule):
    """할일 CRUD 모듈."""

    display_name = "할일 관리"
    description = "할일 등록/조회/완료/삭제"
    supported_intents = [
        "todo.create",
        "todo.list",
        "todo.complete",
        "todo.delete",
    ]

    async def execute(
        self,
        intent: str,
        params: dict[str, Any],
        db: AsyncSession,
    ) -> dict[str, Any]:
        """할일 모듈 실행."""
        action = intent.split(".")[-1]

        if action == "create":
            return await self._create(params, db)
        if action == "list":
            return await self._list(params, db)
        if action == "complete":
            return await self._complete(params, db)
        if action == "delete":
            return await self._delete(params, db)

        return {"message": "지원하지 않는 동작입니다."}

    async def _create(self, params: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
        """할일 생성."""
        title = params.get("title", params.get("raw_text", ""))
        raw_text = params.get("raw_text", "")

        due_date = params.get("due_date")
        if not due_date and raw_text:
            date_start, _ = parse_korean_date(raw_text)
            due_date = date_start.date()

        todo = Todo(
            title=title,
            description=params.get("description"),
            priority=params.get("priority", "normal"),
            due_date=due_date,
            assigned_manager=params.get("assigned_manager"),
        )
        db.add(todo)
        await db.commit()
        await db.refresh(todo)

        return {"id": todo.id, "title": todo.title, "due_date": todo.due_date}

    async def _list(self, params: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
        """할일 목록 조회."""
        query = select(Todo).order_by(Todo.due_date.asc().nulls_last(), Todo.priority.desc())

        # 상태 필터
        status = params.get("status")
        if status:
            query = query.where(Todo.status == status)
        else:
            query = query.where(Todo.status.in_(["pending", "in_progress"]))

        # 날짜 필터
        raw_text = params.get("raw_text", "")
        if raw_text:
            date_start, date_end = parse_korean_date(raw_text)
            query = query.where(Todo.due_date >= date_start.date()).where(Todo.due_date <= date_end.date())

        page = params.get("page", 1)
        items, meta = await paginate(db, query, page=page)

        return {
            "items": [
                {
                    "id": t.id,
                    "title": t.title,
                    "priority": t.priority,
                    "status": t.status,
                    "due_date": t.due_date,
                    "assigned_manager": t.assigned_manager,
                }
                for t in items
            ],
            "meta": meta,
        }

    async def _complete(self, params: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
        """할일 완료 처리."""
        todo_id = params.get("id")
        if not todo_id:
            return {"error": "할일 ID가 필요합니다."}

        result = await db.execute(select(Todo).where(Todo.id == todo_id))
        todo = result.scalar_one_or_none()
        if not todo:
            return {"error": "할일을 찾을 수 없습니다."}

        todo.status = "completed"
        todo.completed_at = datetime.now()
        await db.commit()

        return {"id": todo.id, "title": todo.title, "message": "완료 처리됨"}

    async def _delete(self, params: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
        """할일 삭제 (상태 변경)."""
        todo_id = params.get("id")
        if not todo_id:
            return {"error": "할일 ID가 필요합니다."}

        result = await db.execute(select(Todo).where(Todo.id == todo_id))
        todo = result.scalar_one_or_none()
        if not todo:
            return {"error": "할일을 찾을 수 없습니다."}

        todo.status = "cancelled"
        await db.commit()

        return {"id": todo.id, "message": "삭제 완료"}
