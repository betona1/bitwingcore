"""Bitwing 비즈니스 모듈 — BaseModule 기반 8개 모듈."""

from bitwingcore.modules.base import BaseModule, ModuleRegistry

# 모듈 임포트 시 자동 등록 (@ModuleRegistry.register)
from bitwingcore.modules.calendar_mod import CalendarModule
from bitwingcore.modules.todo_mod import TodoModule
from bitwingcore.modules.memo_mod import MemoModule
from bitwingcore.modules.finance_mod import FinanceModule
from bitwingcore.modules.email_mod import EmailModule
from bitwingcore.modules.file_mod import FileModule
from bitwingcore.modules.pc_manager_mod import PCManagerModule
from bitwingcore.modules.report_mod import ReportModule

__all__ = [
    "BaseModule",
    "ModuleRegistry",
    "CalendarModule",
    "TodoModule",
    "MemoModule",
    "FinanceModule",
    "EmailModule",
    "FileModule",
    "PCManagerModule",
    "ReportModule",
]
