"""Bitwing Core 모듈 베이스 및 레지스트리."""

from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession


class BaseModule(ABC):
    """모든 비즈니스 모듈의 추상 베이스 클래스.

    각 모듈은 이 클래스를 상속하고 @ModuleRegistry.register 데코레이터로 등록한다.
    """

    name: str = ""
    display_name: str = ""
    description: str = ""
    supported_intents: list[str] = []

    @abstractmethod
    async def execute(
        self,
        intent: str,
        params: dict[str, Any],
        db: AsyncSession,
    ) -> dict[str, Any]:
        """모듈 실행 — 의도(intent)에 따라 비즈니스 로직 처리.

        Args:
            intent: 분류된 의도 (예: "schedule.create")
            params: 파싱된 파라미터
            db: DB 세션

        Returns:
            처리 결과 딕셔너리
        """
        ...

    async def get_status(self) -> dict[str, Any]:
        """모듈 상태 반환."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "status": "active",
        }


class ModuleRegistry:
    """모듈 레지스트리 — 등록된 모듈을 관리한다."""

    _modules: dict[str, BaseModule] = {}

    @classmethod
    def register(cls, name: str):
        """모듈 등록 데코레이터.

        사용법:
            @ModuleRegistry.register("calendar_mod")
            class CalendarModule(BaseModule):
                ...
        """
        def decorator(module_cls: type[BaseModule]):
            instance = module_cls()
            instance.name = name
            cls._modules[name] = instance
            return module_cls
        return decorator

    @classmethod
    def get(cls, name: str) -> BaseModule | None:
        """등록된 모듈 조회."""
        return cls._modules.get(name)

    @classmethod
    def list_all(cls) -> list[dict[str, Any]]:
        """전체 모듈 메타데이터 목록."""
        return [
            {
                "name": mod.name,
                "display_name": mod.display_name,
                "description": mod.description,
                "supported_intents": mod.supported_intents,
            }
            for mod in cls._modules.values()
        ]

    @classmethod
    def get_by_intent(cls, intent: str) -> BaseModule | None:
        """의도(intent)에 해당하는 모듈 조회."""
        for mod in cls._modules.values():
            if intent in mod.supported_intents:
                return mod
        return None
