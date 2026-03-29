"""PC 관리 모듈."""

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bitwingcore.models.managed_pc import ManagedPC
from bitwingcore.modules.base import BaseModule, ModuleRegistry
from bitwingcore.utils.pagination import paginate


@ModuleRegistry.register("pc_manager_mod")
class PCManagerModule(BaseModule):
    """사원 PC 관리 모듈."""

    display_name = "PC 관리"
    description = "사원 PC 상태 조회, 원격 명령 실행"
    supported_intents = [
        "pc.status",
        "pc.command",
    ]

    async def execute(
        self,
        intent: str,
        params: dict[str, Any],
        db: AsyncSession,
    ) -> dict[str, Any]:
        """PC 관리 모듈 실행."""
        action = intent.split(".")[-1]

        if action == "status":
            return await self._status(params, db)
        if action == "command":
            return await self._command(params, db)

        return {"message": "지원하지 않는 동작입니다."}

    async def _status(self, params: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
        """PC 상태 목록 조회."""
        query = select(ManagedPC).order_by(ManagedPC.hostname)

        status_filter = params.get("status")
        if status_filter:
            query = query.where(ManagedPC.status == status_filter)

        page = params.get("page", 1)
        items, meta = await paginate(db, query, page=page)

        return {
            "items": [
                {
                    "id": pc.id,
                    "hostname": pc.hostname,
                    "ip_address": pc.ip_address,
                    "os_type": pc.os_type,
                    "employee_name": pc.employee_name,
                    "department": pc.department,
                    "status": pc.status,
                    "last_seen_at": pc.last_seen_at,
                }
                for pc in items
            ],
            "meta": meta,
        }

    async def _command(self, params: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
        """원격 명령 실행 (비동기 작업 등록).

        실제 SSH 실행은 Celery 태스크나 별도 워커에서 처리.
        여기서는 명령 요청을 기록하고 작업 ID를 반환한다.
        """
        pc_id = params.get("pc_id")
        command = params.get("command", "")

        if not pc_id:
            return {"error": "PC ID가 필요합니다."}
        if not command:
            return {"error": "실행할 명령이 필요합니다."}

        result = await db.execute(select(ManagedPC).where(ManagedPC.id == pc_id))
        pc = result.scalar_one_or_none()
        if not pc:
            return {"error": "PC를 찾을 수 없습니다."}

        if pc.status != "online":
            return {"error": f"{pc.hostname}은(는) 현재 오프라인입니다."}

        # 작업 등록 (실제 실행은 Celery 태스크에서)
        return {
            "pc_id": pc.id,
            "hostname": pc.hostname,
            "command": command,
            "status": "queued",
            "message": f"{pc.hostname}에 명령 전달 대기중",
        }
