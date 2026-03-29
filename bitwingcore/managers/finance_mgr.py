"""재무 매니저 — 가계부, 은행 연동, OCR."""

from bitwingcore.managers.base import BaseManager


class FinanceManager(BaseManager):
    """재무 전담 매니저."""

    code_name = "finance_mgr"
    display_name = "재무 매니저"
    role = "가계부 관리, 수입/지출 기록, 은행 연동, 영수증 OCR"
    managed_modules = ["finance_mod"]
