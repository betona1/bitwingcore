"""일정 API — 캘린더 CRUD."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bitwingcore.api.schemas import CalendarCreate, CalendarUpdate
from bitwingcore.auth import verify_api_key
from bitwingcore.database import get_db
from bitwingcore.models.calendar import Calendar
from bitwingcore.utils.date_parser import parse_korean_date
from bitwingcore.utils.pagination import paginate
from bitwingcore.utils.response import error_response, success_response

router = APIRouter(prefix="/calendars", tags=["calendars"])


@router.get("")
async def list_calendars(
    date_range: str = "이번주",
    page: int = 1,
    size: int = 50,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """일정 목록 조회."""
    date_start, date_end = parse_korean_date(date_range)

    query = (
        select(Calendar)
        .where(Calendar.start_at >= date_start)
        .where(Calendar.start_at <= date_end)
        .where(Calendar.status == "active")
        .order_by(Calendar.start_at)
    )
    items, meta = await paginate(db, query, page=page, size=size)

    return success_response(
        data={
            "items": [
                {
                    "id": e.id,
                    "title": e.title,
                    "description": e.description,
                    "start_at": str(e.start_at),
                    "end_at": str(e.end_at),
                    "location": e.location,
                    "status": e.status,
                    "google_event_id": e.google_event_id,
                }
                for e in items
            ],
            "meta": meta,
        }
    )


@router.get("/{calendar_id}")
async def get_calendar(
    calendar_id: int,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """일정 상세 조회."""
    result = await db.execute(select(Calendar).where(Calendar.id == calendar_id))
    event = result.scalar_one_or_none()
    if not event:
        error_response("일정을 찾을 수 없습니다.", 404)

    return success_response(
        data={
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "start_at": str(event.start_at),
            "end_at": str(event.end_at),
            "location": event.location,
            "reminder_minutes": event.reminder_minutes,
            "status": event.status,
            "google_event_id": event.google_event_id,
            "source": event.source,
        }
    )


@router.post("")
async def create_calendar(
    req: CalendarCreate,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """일정 생성."""
    event = Calendar(
        title=req.title,
        description=req.description,
        start_at=req.start_at,
        end_at=req.end_at,
        location=req.location,
        reminder_minutes=req.reminder_minutes,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)

    return success_response(
        data={"id": event.id, "title": event.title},
        message="일정을 등록했습니다.",
    )


@router.put("/{calendar_id}")
async def update_calendar(
    calendar_id: int,
    req: CalendarUpdate,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """일정 수정."""
    result = await db.execute(select(Calendar).where(Calendar.id == calendar_id))
    event = result.scalar_one_or_none()
    if not event:
        error_response("일정을 찾을 수 없습니다.", 404)

    update_data = req.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)

    await db.commit()
    return success_response(message="일정을 수정했습니다.")


@router.delete("/{calendar_id}")
async def delete_calendar(
    calendar_id: int,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """일정 삭제 (상태 변경)."""
    result = await db.execute(select(Calendar).where(Calendar.id == calendar_id))
    event = result.scalar_one_or_none()
    if not event:
        error_response("일정을 찾을 수 없습니다.", 404)

    event.status = "cancelled"
    await db.commit()
    return success_response(message="일정을 삭제했습니다.")
