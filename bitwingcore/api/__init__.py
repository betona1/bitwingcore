"""Bitwing Core REST API 라우터."""

from bitwingcore.api.calendar_api import router as calendar_router
from bitwingcore.api.chat import router as chat_router
from bitwingcore.api.email_api import router as email_router
from bitwingcore.api.file_api import router as file_router
from bitwingcore.api.finance_api import router as finance_router
from bitwingcore.api.integration_api import router as integration_router
from bitwingcore.api.manager_api import router as manager_router
from bitwingcore.api.memo_api import router as memo_router
from bitwingcore.api.pc_api import router as pc_router
from bitwingcore.api.report_api import router as report_router
from bitwingcore.api.todo_api import router as todo_router

ALL_ROUTERS = [
    chat_router,
    manager_router,
    calendar_router,
    todo_router,
    memo_router,
    finance_router,
    email_router,
    file_router,
    pc_router,
    report_router,
    integration_router,
]
