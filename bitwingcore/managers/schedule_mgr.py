"""일정 매니저 — 캘린더, Google Calendar 연동."""

from bitwingcore.managers.base import BaseManager


class ScheduleManager(BaseManager):
    """일정 전담 매니저."""

    code_name = "schedule_mgr"
    display_name = "일정 매니저"
    role = "캘린더 일정 등록/조회/수정/삭제, Google Calendar 동기화"
    managed_modules = ["calendar_mod"]
