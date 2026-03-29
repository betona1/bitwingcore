"""Celery 앱 설정 — Redis 브로커, Beat 스케줄."""

from celery import Celery
from celery.schedules import crontab

from bitwingcore.config import get_settings

settings = get_settings()

celery_app = Celery(
    "bitwing",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Seoul",
    enable_utc=False,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Beat 스케줄 (정기 작업)
celery_app.conf.beat_schedule = {
    # 일일 보고 — 매일 22:00
    "daily-report": {
        "task": "bitwingcore.tasks.scheduled.generate_daily_report",
        "schedule": crontab(hour=22, minute=0),
    },
    # 이메일 동기화 — 30분마다
    "email-sync": {
        "task": "bitwingcore.tasks.scheduled.sync_emails",
        "schedule": crontab(minute="*/30"),
    },
    # PC 상태 체크 — 10분마다
    "pc-health-check": {
        "task": "bitwingcore.tasks.scheduled.check_pc_status",
        "schedule": crontab(minute="*/10"),
    },
    # 캘린더 리마인더 — 5분마다
    "calendar-reminder": {
        "task": "bitwingcore.tasks.scheduled.send_calendar_reminders",
        "schedule": crontab(minute="*/5"),
    },
}

# 태스크 자동 발견
celery_app.autodiscover_tasks(["bitwingcore.tasks"])
