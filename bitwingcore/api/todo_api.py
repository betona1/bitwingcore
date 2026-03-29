"""할일 API — Todo CRUD."""

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bitwingcore.api.schemas import TodoCreate, TodoUpdate
from bitwingcore.auth import verify_api_key
from bitwingcore.database import get_db
from bitwingcore.models.todo import Todo
from bitwingcore.utils.pagination import paginate
from bitwingcore.utils.response import error_response, success_response

router = APIRouter(prefix="/todos", tags=["todos"])


@router.get("")
async def list_todos(
    status: str | None = None,
    priority: str | None = None,
    page: int = 1,
    size: int = 50,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """할일 목록 조회."""
    query = select(Todo).order_by(Todo.due_date.asc().nulls_last())

    if status:
        query = query.where(Todo.status == status)
    else:
        query = query.where(Todo.status.in_(["pending", "in_progress"]))

    if priority:
        query = query.where(Todo.priority == priority)

    items, meta = await paginate(db, query, page=page, size=size)

    return success_response(
        data={
            "items": [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "priority": t.priority,
                    "status": t.status,
                    "due_date": str(t.due_date) if t.due_date else None,
                    "assigned_manager": t.assigned_manager,
                    "created_at": str(t.created_at),
                }
                for t in items
            ],
            "meta": meta,
        }
    )


@router.get("/{todo_id}")
async def get_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """할일 상세 조회."""
    result = await db.execute(select(Todo).where(Todo.id == todo_id))
    todo = result.scalar_one_or_none()
    if not todo:
        error_response("할일을 찾을 수 없습니다.", 404)

    return success_response(
        data={
            "id": todo.id,
            "title": todo.title,
            "description": todo.description,
            "priority": todo.priority,
            "status": todo.status,
            "due_date": str(todo.due_date) if todo.due_date else None,
            "assigned_manager": todo.assigned_manager,
            "completed_at": str(todo.completed_at) if todo.completed_at else None,
        }
    )


@router.post("")
async def create_todo(
    req: TodoCreate,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """할일 생성."""
    todo = Todo(
        title=req.title,
        description=req.description,
        priority=req.priority,
        due_date=req.due_date,
        assigned_manager=req.assigned_manager,
    )
    db.add(todo)
    await db.commit()
    await db.refresh(todo)

    return success_response(
        data={"id": todo.id, "title": todo.title},
        message="할일을 등록했습니다.",
    )


@router.put("/{todo_id}")
async def update_todo(
    todo_id: int,
    req: TodoUpdate,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """할일 수정."""
    result = await db.execute(select(Todo).where(Todo.id == todo_id))
    todo = result.scalar_one_or_none()
    if not todo:
        error_response("할일을 찾을 수 없습니다.", 404)

    update_data = req.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(todo, field, value)

    if req.status == "completed" and not todo.completed_at:
        todo.completed_at = datetime.now()

    await db.commit()
    return success_response(message="할일을 수정했습니다.")


@router.post("/{todo_id}/complete")
async def complete_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """할일 완료 처리."""
    result = await db.execute(select(Todo).where(Todo.id == todo_id))
    todo = result.scalar_one_or_none()
    if not todo:
        error_response("할일을 찾을 수 없습니다.", 404)

    todo.status = "completed"
    todo.completed_at = datetime.now()
    await db.commit()

    return success_response(message="할일을 완료 처리했습니다.")


@router.delete("/{todo_id}")
async def delete_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """할일 삭제."""
    result = await db.execute(select(Todo).where(Todo.id == todo_id))
    todo = result.scalar_one_or_none()
    if not todo:
        error_response("할일을 찾을 수 없습니다.", 404)

    todo.status = "cancelled"
    await db.commit()
    return success_response(message="할일을 삭제했습니다.")
