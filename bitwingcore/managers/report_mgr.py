"""보고 매니저 — 리포트, 통계 분석."""

from bitwingcore.managers.base import BaseManager


class ReportManager(BaseManager):
    """보고 전담 매니저."""

    code_name = "report_mgr"
    display_name = "보고 매니저"
    role = "일일/주간/월간 리포트 생성, 통계 분석"
    managed_modules = ["report_mod"]
