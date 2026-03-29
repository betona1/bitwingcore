"""매니저 디스패처 — intent를 적절한 매니저에게 라우팅."""

from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bitwingcore.managers.base import BaseManager
from bitwingcore.managers.finance_mgr import FinanceManager
from bitwingcore.managers.it_mgr import ITManager
from bitwingcore.managers.report_mgr import ReportManager
from bitwingcore.managers.schedule_mgr import ScheduleManager
from bitwingcore.managers.task_mgr import TaskManager

# 매니저 코드명 → 인스턴스 매핑
_MANAGERS: dict[str, BaseManager] = {
    "schedule_mgr": ScheduleManager(),
    "task_mgr": TaskManager(),
    "finance_mgr": FinanceManager(),
    "it_mgr": ITManager(),
    "report_mgr": ReportManager(),
}


async def dispatch(
    manager_name: str,
    intent: str,
    params: dict[str, Any],
    db: AsyncSession,
) -> dict[str, Any]:
    """의도를 적절한 매니저에게 디스패치.

    Args:
        manager_name: 매니저 코드명 (예: "schedule_mgr")
        intent: 의도 코드 (예: "schedule.create")
        params: 파라미터 딕셔너리
        db: DB 세션

    Returns:
        매니저 처리 결과
    """
    manager = _MANAGERS.get(manager_name)
    if not manager:
        logger.error(f"매니저를 찾을 수 없습니다: {manager_name}")
        return {"error": f"매니저 '{manager_name}'을(를) 찾을 수 없습니다."}

    logger.info(f"디스패치: {intent} → {manager_name} ({manager.display_name})")
    return await manager.handle(intent, params, db)


def get_manager(name: str) -> BaseManager | None:
    """매니저 인스턴스 조회."""
    return _MANAGERS.get(name)


def list_managers() -> list[dict[str, Any]]:
    """전체 매니저 목록 반환."""
    return [
        {
            "code_name": mgr.code_name,
            "display_name": mgr.display_name,
            "role": mgr.role,
            "managed_modules": mgr.managed_modules,
        }
        for mgr in _MANAGERS.values()
    ]
