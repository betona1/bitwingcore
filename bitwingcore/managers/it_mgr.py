"""IT 매니저 — 사원 PC 관리, AI100 연동."""

from bitwingcore.managers.base import BaseManager


class ITManager(BaseManager):
    """IT 전담 매니저."""

    code_name = "it_mgr"
    display_name = "IT 매니저"
    role = "사원 PC 관리, 원격 명령 실행, 시스템 상태 모니터링"
    managed_modules = ["pc_manager_mod"]
