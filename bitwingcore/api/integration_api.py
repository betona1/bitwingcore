"""연동 API — 외부 서비스 연동 관리."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bitwingcore.api.schemas import IntegrationCreate
from bitwingcore.auth import verify_api_key
from bitwingcore.database import get_db
from bitwingcore.models.integration import Integration
from bitwingcore.utils.pagination import paginate
from bitwingcore.utils.response import error_response, success_response

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("")
async def list_integrations(
    page: int = 1,
    size: int = 50,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """연동 서비스 목록 조회."""
    query = select(Integration).order_by(Integration.created_at.desc())
    items, meta = await paginate(db, query, page=page, size=size)

    return success_response(
        data={
            "items": [
                {
                    "id": i.id,
                    "service": i.service,
                    "status": i.status,
                    "last_synced_at": str(i.last_synced_at) if i.last_synced_at else None,
                }
                for i in items
            ],
            "meta": meta,
        }
    )


@router.post("")
async def create_integration(
    req: IntegrationCreate,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """연동 설정 추가."""
    integration = Integration(
        service=req.service,
        config=req.config,
    )
    db.add(integration)
    await db.commit()
    await db.refresh(integration)

    return success_response(
        data={"id": integration.id, "service": integration.service},
        message="연동 설정을 추가했습니다.",
    )


@router.delete("/{integration_id}")
async def delete_integration(
    integration_id: int,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """연동 설정 삭제."""
    result = await db.execute(select(Integration).where(Integration.id == integration_id))
    integration = result.scalar_one_or_none()
    if not integration:
        error_response("연동 설정을 찾을 수 없습니다.", 404)

    await db.delete(integration)
    await db.commit()
    return success_response(message="연동 설정을 삭제했습니다.")
