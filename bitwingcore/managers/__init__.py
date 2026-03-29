"""Bitwing AI 매니저 — 5명의 전담 매니저 + 디스패처."""

from bitwingcore.managers.dispatcher import dispatch, get_manager, list_managers
from bitwingcore.managers.finance_mgr import FinanceManager
from bitwingcore.managers.it_mgr import ITManager
from bitwingcore.managers.report_mgr import ReportManager
from bitwingcore.managers.schedule_mgr import ScheduleManager
from bitwingcore.managers.task_mgr import TaskManager

__all__ = [
    "dispatch",
    "get_manager",
    "list_managers",
    "ScheduleManager",
    "TaskManager",
    "FinanceManager",
    "ITManager",
    "ReportManager",
]
