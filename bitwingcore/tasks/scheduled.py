"""Celery 정기 작업 — 리마인더, 일일보고, 이메일 동기화, PC 상태 체크."""

from datetime import datetime, timedelta

from loguru import logger

from bitwingcore.celery_app import celery_app


@celery_app.task(name="bitwingcore.tasks.scheduled.generate_daily_report")
def generate_daily_report() -> dict:
    """일일 보고 생성 및 텔레그램 발송.

    매일 22:00 실행. 오늘 일정/할일/지출 요약을 생성하여 텔레그램으로 전송한다.
    """
    import asyncio
    from bitwingcore.database import async_session
    from bitwingcore.modules.report_mod import ReportModule
    from bitwingcore.utils.telegram import send_telegram

    async def _run() -> dict:
        report_mod = ReportModule()
        async with async_session() as db:
            result = await report_mod.execute("report.daily", {}, db)
            report_text = result.get("report_text", "리포트 생성 실패")

            # 텔레그램 발송
            await send_telegram(report_text)
            logger.info("일일 보고 텔레그램 발송 완료")
            return result

    return asyncio.get_event_loop().run_until_complete(_run())


@celery_app.task(name="bitwingcore.tasks.scheduled.sync_emails")
def sync_emails() -> dict:
    """이메일 동기화.

    30분마다 실행. Gmail/IMAP에서 새 이메일을 가져와 email_cache에 저장한다.
    """
    # Phase 4.2에서 Gmail 연동 구현 후 활성화
    logger.info("이메일 동기화 실행 (스텁)")
    return {"status": "stub", "message": "Phase 4.2에서 구현 예정"}


@celery_app.task(name="bitwingcore.tasks.scheduled.check_pc_status")
def check_pc_status() -> dict:
    """사원 PC 상태 체크.

    10분마다 실행. 등록된 PC의 온라인 상태를 확인하고 DB를 업데이트한다.
    """
    import asyncio
    from sqlalchemy import select
    from bitwingcore.database import async_session
    from bitwingcore.models.managed_pc import ManagedPC

    async def _run() -> dict:
        import subprocess

        async with async_session() as db:
            result = await db.execute(select(ManagedPC))
            pcs = list(result.scalars().all())
            updated = 0

            for pc in pcs:
                if not pc.ip_address:
                    continue

                # ping 체크
                try:
                    ret = subprocess.run(
                        ["ping", "-c", "1", "-W", "2", pc.ip_address],
                        capture_output=True, timeout=5,
                    )
                    new_status = "online" if ret.returncode == 0 else "offline"
                except Exception:
                    new_status = "offline"

                if pc.status != new_status:
                    pc.status = new_status
                    if new_status == "online":
                        pc.last_seen_at = datetime.now()
                    updated += 1

            await db.commit()
            logger.info(f"PC 상태 체크 완료: {len(pcs)}대 중 {updated}대 업데이트")
            return {"total": len(pcs), "updated": updated}

    return asyncio.get_event_loop().run_until_complete(_run())


@celery_app.task(name="bitwingcore.tasks.scheduled.send_calendar_reminders")
def send_calendar_reminders() -> dict:
    """캘린더 리마인더 발송.

    5분마다 실행. 곧 시작되는 일정의 리마인더를 텔레그램으로 발송한다.
    """
    import asyncio
    from sqlalchemy import select
    from bitwingcore.database import async_session
    from bitwingcore.models.calendar import Calendar
    from bitwingcore.utils.telegram import send_telegram

    async def _run() -> dict:
        now = datetime.now()
        sent = 0

        async with async_session() as db:
            # 30분 이내 시작 일정 조회
            result = await db.execute(
                select(Calendar)
                .where(Calendar.status == "active")
                .where(Calendar.start_at > now)
                .where(Calendar.start_at <= now + timedelta(minutes=30))
            )
            events = list(result.scalars().all())

            for event in events:
                minutes_left = int((event.start_at - now).total_seconds() / 60)
                if minutes_left <= event.reminder_minutes:
                    msg = f"[리마인더] {event.title}\n{event.start_at.strftime('%H:%M')} ({minutes_left}분 후)"
                    if event.location:
                        msg += f"\n장소: {event.location}"
                    await send_telegram(msg)
                    sent += 1

        logger.info(f"캘린더 리마인더: {sent}건 발송")
        return {"sent": sent}

    return asyncio.get_event_loop().run_until_complete(_run())
