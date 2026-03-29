"""AI 매니저 베이스 클래스."""

import time
from datetime import datetime
from typing import Any

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bitwingcore.models.manager import Manager
from bitwingcore.models.manager_task import ManagerTask


class BaseManager:
    """모든 AI 매니저의 베이스 클래스.

    각 매니저는 특정 도메인(일정, 업무, 재무 등)을 전담 처리한다.
    """

    code_name: str = ""
    display_name: str = ""
    role: str = ""
    managed_modules: list[str] = []

    async def handle(
        self,
        intent: str,
        params: dict[str, Any],
        db: AsyncSession,
    ) -> dict[str, Any]:
        """요청을 처리하고 결과를 반환.

        Args:
            intent: 의도 코드 (예: "schedule.create")
            params: 파싱된 파라미터
            db: DB 세션

        Returns:
            처리 결과 딕셔너리
        """
        start_time = time.time()

        # 매니저 작업 기록 시작
        task = ManagerTask(
            manager=self.code_name,
            intent=intent,
            request=params.get("raw_text", ""),
            status="processing",
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)

        try:
            # 해당 모듈 찾아서 실행
            from bitwingcore.modules.base import ModuleRegistry

            module = ModuleRegistry.get_by_intent(intent)
            if not module:
                raise ValueError(f"의도 '{intent}'를 처리할 모듈이 없습니다.")

            result = await module.execute(intent, params, db)

            # 작업 완료 기록
            duration_ms = int((time.time() - start_time) * 1000)
            task.status = "completed"
            task.response = str(result)[:2000]
            task.duration_ms = duration_ms
            task.completed_at = datetime.now()
            await db.commit()

            # 매니저 총 작업 수 업데이트
            await self._update_stats(db)

            logger.info(
                f"[{self.code_name}] {intent} 처리 완료 ({duration_ms}ms)"
            )
            return result

        except Exception as e:
            task.status = "failed"
            task.response = str(e)[:2000]
            task.duration_ms = int((time.time() - start_time) * 1000)
            await db.commit()

            logger.error(f"[{self.code_name}] {intent} 처리 실패: {e}")
            return {"error": str(e)}

    async def get_status(self, db: AsyncSession) -> dict[str, Any]:
        """매니저 상태 조회."""
        result = await db.execute(
            select(Manager).where(Manager.name == self.code_name)
        )
        mgr = result.scalar_one_or_none()

        return {
            "code_name": self.code_name,
            "display_name": self.display_name,
            "status": mgr.status if mgr else "unknown",
            "total_tasks": mgr.total_tasks if mgr else 0,
            "last_active_at": mgr.last_active_at if mgr else None,
            "managed_modules": self.managed_modules,
        }

    async def _update_stats(self, db: AsyncSession) -> None:
        """매니저 통계 업데이트."""
        result = await db.execute(
            select(Manager).where(Manager.name == self.code_name)
        )
        mgr = result.scalar_one_or_none()
        if mgr:
            mgr.total_tasks = (mgr.total_tasks or 0) + 1
            mgr.last_active_at = datetime.now()
            await db.commit()
