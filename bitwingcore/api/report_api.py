"""리포트 API — 일일/주간/월간 리포트."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from bitwingcore.auth import verify_api_key
from bitwingcore.database import get_db
from bitwingcore.modules.report_mod import ReportModule
from bitwingcore.utils.response import success_response

router = APIRouter(prefix="/reports", tags=["reports"])

_report_mod = ReportModule()


@router.get("/daily")
async def daily_report(
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """일일 리포트 생성."""
    result = await _report_mod.execute("report.daily", {}, db)
    return success_response(data=result, message="일일 리포트를 생성했습니다.")


@router.get("/weekly")
async def weekly_report(
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """주간 리포트 생성."""
    result = await _report_mod.execute("report.weekly", {}, db)
    return success_response(data=result, message="주간 리포트를 생성했습니다.")


@router.get("/monthly")
async def monthly_report(
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """월간 리포트 생성."""
    result = await _report_mod.execute("report.monthly", {}, db)
    return success_response(data=result, message="월간 리포트를 생성했습니다.")
