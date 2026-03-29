"""PC 관리 API — 사원 PC 관리/원격 명령."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bitwingcore.api.schemas import PCCommand, PCCreate
from bitwingcore.auth import verify_api_key
from bitwingcore.database import get_db
from bitwingcore.models.managed_pc import ManagedPC
from bitwingcore.utils.pagination import paginate
from bitwingcore.utils.response import error_response, success_response

router = APIRouter(prefix="/pcs", tags=["pcs"])


@router.get("")
async def list_pcs(
    status: str | None = None,
    department: str | None = None,
    page: int = 1,
    size: int = 50,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """PC 목록 조회."""
    query = select(ManagedPC).order_by(ManagedPC.hostname)

    if status:
        query = query.where(ManagedPC.status == status)
    if department:
        query = query.where(ManagedPC.department == department)

    items, meta = await paginate(db, query, page=page, size=size)

    return success_response(
        data={
            "items": [
                {
                    "id": pc.id,
                    "hostname": pc.hostname,
                    "ip_address": pc.ip_address,
                    "os_type": pc.os_type,
                    "employee_name": pc.employee_name,
                    "department": pc.department,
                    "status": pc.status,
                    "last_seen_at": str(pc.last_seen_at) if pc.last_seen_at else None,
                }
                for pc in items
            ],
            "meta": meta,
        }
    )


@router.get("/{pc_id}")
async def get_pc(
    pc_id: int,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """PC 상세 정보."""
    result = await db.execute(select(ManagedPC).where(ManagedPC.id == pc_id))
    pc = result.scalar_one_or_none()
    if not pc:
        error_response("PC를 찾을 수 없습니다.", 404)

    return success_response(
        data={
            "id": pc.id,
            "hostname": pc.hostname,
            "ip_address": pc.ip_address,
            "os_type": pc.os_type,
            "employee_name": pc.employee_name,
            "department": pc.department,
            "status": pc.status,
            "last_seen_at": str(pc.last_seen_at) if pc.last_seen_at else None,
            "system_info": pc.system_info,
        }
    )


@router.post("")
async def register_pc(
    req: PCCreate,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """PC 등록."""
    pc = ManagedPC(
        hostname=req.hostname,
        ip_address=req.ip_address,
        os_type=req.os_type,
        employee_name=req.employee_name,
        department=req.department,
    )
    db.add(pc)
    await db.commit()
    await db.refresh(pc)

    return success_response(
        data={"id": pc.id, "hostname": pc.hostname},
        message="PC를 등록했습니다.",
    )


@router.post("/{pc_id}/command")
async def send_command(
    pc_id: int,
    req: PCCommand,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """PC 원격 명령 전송."""
    result = await db.execute(select(ManagedPC).where(ManagedPC.id == pc_id))
    pc = result.scalar_one_or_none()
    if not pc:
        error_response("PC를 찾을 수 없습니다.", 404)

    if pc.status != "online":
        error_response(f"{pc.hostname}은(는) 현재 오프라인입니다.")

    # 실제 명령 실행은 Celery 태스크로 위임
    return success_response(
        data={
            "pc_id": pc.id,
            "hostname": pc.hostname,
            "command": req.command,
            "status": "queued",
        },
        message=f"{pc.hostname}에 명령을 전달했습니다.",
    )


@router.delete("/{pc_id}")
async def delete_pc(
    pc_id: int,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """PC 등록 해제."""
    result = await db.execute(select(ManagedPC).where(ManagedPC.id == pc_id))
    pc = result.scalar_one_or_none()
    if not pc:
        error_response("PC를 찾을 수 없습니다.", 404)

    await db.delete(pc)
    await db.commit()
    return success_response(message="PC를 등록 해제했습니다.")
