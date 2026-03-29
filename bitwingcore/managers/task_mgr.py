"""업무 매니저 — 할일, 메모, 이메일, 파일."""

from bitwingcore.managers.base import BaseManager


class TaskManager(BaseManager):
    """업무 전담 매니저."""

    code_name = "task_mgr"
    display_name = "업무 매니저"
    role = "할일 관리, 메모, 이메일 확인, 파일 관리"
    managed_modules = ["todo_mod", "memo_mod", "email_mod", "file_mod"]
