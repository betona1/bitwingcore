"""매니저 API — 매니저 조회/상태 확인."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bitwingcore.auth import verify_api_key
from bitwingcore.database import get_db
from bitwingcore.managers.dispatcher import get_manager, list_managers
from bitwingcore.models.manager import Manager
from bitwingcore.models.manager_task import ManagerTask
from bitwingcore.utils.pagination import paginate
from bitwingcore.utils.response import error_response, success_response

router = APIRouter(prefix="/managers", tags=["managers"])


@router.get("")
async def get_managers(
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """전체 매니저 목록 조회."""
    return success_response(data=list_managers())


@router.get("/{manager_name}")
async def get_manager_detail(
    manager_name: str,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """매니저 상세 정보."""
    mgr = get_manager(manager_name)
    if not mgr:
        error_response(f"매니저 '{manager_name}'을(를) 찾을 수 없습니다.", 404)

    status = await mgr.get_status(db)
    return success_response(data=status)


@router.get("/{manager_name}/tasks")
async def get_manager_tasks(
    manager_name: str,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """매니저 작업 히스토리 조회."""
    query = (
        select(ManagerTask)
        .where(ManagerTask.manager == manager_name)
        .order_by(ManagerTask.created_at.desc())
    )
    items, meta = await paginate(db, query, page=page, size=size)

    return success_response(
        data={
            "items": [
                {
                    "id": t.id,
                    "intent": t.intent,
                    "request": t.request,
                    "response": t.response,
                    "status": t.status,
                    "duration_ms": t.duration_ms,
                    "created_at": str(t.created_at) if t.created_at else None,
                }
                for t in items
            ],
            "meta": meta,
        }
    )
