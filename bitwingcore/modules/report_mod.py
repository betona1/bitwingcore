"""리포트 생성 모듈."""

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bitwingcore.models.calendar import Calendar
from bitwingcore.models.finance_transaction import FinanceTransaction
from bitwingcore.models.manager_task import ManagerTask
from bitwingcore.models.todo import Todo
from bitwingcore.modules.base import BaseModule, ModuleRegistry


@ModuleRegistry.register("report_mod")
class ReportModule(BaseModule):
    """일일/주간/월간 리포트 생성 모듈."""

    display_name = "리포트"
    description = "일일, 주간, 월간 리포트 생성"
    supported_intents = [
        "report.daily",
        "report.weekly",
        "report.monthly",
    ]

    async def execute(
        self,
        intent: str,
        params: dict[str, Any],
        db: AsyncSession,
    ) -> dict[str, Any]:
        """리포트 모듈 실행."""
        action = intent.split(".")[-1]

        if action == "daily":
            return await self._daily(params, db)
        if action == "weekly":
            return await self._weekly(params, db)
        if action == "monthly":
            return await self._monthly(params, db)

        return {"message": "지원하지 않는 동작입니다."}

    async def _daily(self, params: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
        """일일 리포트 생성."""
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=0)

        # 오늘 일정
        schedules = await db.execute(
            select(Calendar)
            .where(Calendar.start_at >= today_start, Calendar.start_at <= today_end)
            .where(Calendar.status == "active")
            .order_by(Calendar.start_at)
        )
        schedule_list = list(schedules.scalars().all())

        # 오늘 할일
        todos = await db.execute(
            select(Todo)
            .where(Todo.due_date == today_start.date())
            .where(Todo.status.in_(["pending", "in_progress", "completed"]))
        )
        todo_list = list(todos.scalars().all())

        # 오늘 매니저 작업
        tasks = await db.execute(
            select(func.count(ManagerTask.id), ManagerTask.status)
            .where(ManagerTask.created_at >= today_start)
            .group_by(ManagerTask.status)
        )
        task_stats = {row[1]: row[0] for row in tasks.all()}

        # 오늘 지출
        expense = await db.execute(
            select(func.coalesce(func.sum(FinanceTransaction.amount), 0))
            .where(FinanceTransaction.transaction_date == today_start.date())
            .where(FinanceTransaction.type == "expense")
        )
        total_expense = float(expense.scalar() or 0)

        # 리포트 텍스트 조합
        lines = [f"=== 일일 리포트 ({now.strftime('%Y년 %m월 %d일')}) ==="]
        lines.append("")

        # 일정
        lines.append(f"[일정] {len(schedule_list)}건")
        for s in schedule_list[:5]:
            lines.append(f"  - {s.start_at.strftime('%H:%M')} {s.title}")

        # 할일
        completed = sum(1 for t in todo_list if t.status == "completed")
        lines.append(f"\n[할일] {len(todo_list)}건 (완료: {completed}건)")
        for t in todo_list[:5]:
            mark = "[v]" if t.status == "completed" else "[ ]"
            lines.append(f"  {mark} {t.title}")

        # 매니저 작업
        total_tasks = sum(task_stats.values())
        lines.append(f"\n[매니저 작업] {total_tasks}건 처리")

        # 지출
        lines.append(f"\n[오늘 지출] {total_expense:,.0f}원")

        report_text = "\n".join(lines)

        return {
            "report_text": report_text,
            "date": now.strftime("%Y-%m-%d"),
            "schedule_count": len(schedule_list),
            "todo_count": len(todo_list),
            "todo_completed": completed,
            "task_stats": task_stats,
            "total_expense": total_expense,
        }

    async def _weekly(self, params: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
        """주간 리포트 생성."""
        now = datetime.now()
        monday = now - timedelta(days=now.weekday())
        week_start = monday.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = (monday + timedelta(days=6)).replace(hour=23, minute=59, second=59)

        # 이번주 할일 완료율
        todo_result = await db.execute(
            select(
                func.count(Todo.id),
                func.sum(func.IF(Todo.status == "completed", 1, 0)),
            )
            .where(Todo.due_date >= week_start.date())
            .where(Todo.due_date <= week_end.date())
        )
        row = todo_result.one()
        total_todos = row[0] or 0
        completed_todos = int(row[1] or 0)

        # 이번주 지출 합계
        expense_result = await db.execute(
            select(func.coalesce(func.sum(FinanceTransaction.amount), 0))
            .where(FinanceTransaction.transaction_date >= week_start.date())
            .where(FinanceTransaction.transaction_date <= week_end.date())
            .where(FinanceTransaction.type == "expense")
        )
        total_expense = float(expense_result.scalar() or 0)

        # 매니저 작업 통계
        task_result = await db.execute(
            select(ManagerTask.manager, func.count(ManagerTask.id))
            .where(ManagerTask.created_at >= week_start)
            .group_by(ManagerTask.manager)
        )
        manager_stats = {row[0]: row[1] for row in task_result.all()}

        lines = [f"=== 주간 리포트 ({week_start.strftime('%m/%d')}~{week_end.strftime('%m/%d')}) ==="]
        lines.append(f"\n[할일] {total_todos}건 중 {completed_todos}건 완료")
        lines.append(f"[주간 지출] {total_expense:,.0f}원")
        lines.append(f"\n[매니저별 처리]")
        for mgr, count in manager_stats.items():
            lines.append(f"  - {mgr}: {count}건")

        return {
            "report_text": "\n".join(lines),
            "week_start": week_start.strftime("%Y-%m-%d"),
            "week_end": week_end.strftime("%Y-%m-%d"),
            "total_todos": total_todos,
            "completed_todos": completed_todos,
            "total_expense": total_expense,
            "manager_stats": manager_stats,
        }

    async def _monthly(self, params: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
        """월간 리포트 생성."""
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            month_end = now.replace(year=now.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = now.replace(month=now.month + 1, day=1) - timedelta(days=1)
        month_end = month_end.replace(hour=23, minute=59, second=59)

        # 월간 수입/지출
        income_result = await db.execute(
            select(func.coalesce(func.sum(FinanceTransaction.amount), 0))
            .where(FinanceTransaction.transaction_date >= month_start.date())
            .where(FinanceTransaction.transaction_date <= month_end.date())
            .where(FinanceTransaction.type == "income")
        )
        total_income = float(income_result.scalar() or 0)

        expense_result = await db.execute(
            select(func.coalesce(func.sum(FinanceTransaction.amount), 0))
            .where(FinanceTransaction.transaction_date >= month_start.date())
            .where(FinanceTransaction.transaction_date <= month_end.date())
            .where(FinanceTransaction.type == "expense")
        )
        total_expense = float(expense_result.scalar() or 0)

        # 카테고리별 지출
        cat_result = await db.execute(
            select(FinanceTransaction.category, func.sum(FinanceTransaction.amount))
            .where(FinanceTransaction.transaction_date >= month_start.date())
            .where(FinanceTransaction.transaction_date <= month_end.date())
            .where(FinanceTransaction.type == "expense")
            .group_by(FinanceTransaction.category)
            .order_by(func.sum(FinanceTransaction.amount).desc())
        )
        categories = {row[0]: float(row[1]) for row in cat_result.all()}

        lines = [f"=== 월간 리포트 ({now.strftime('%Y년 %m월')}) ==="]
        lines.append(f"\n[수입] {total_income:,.0f}원")
        lines.append(f"[지출] {total_expense:,.0f}원")
        lines.append(f"[잔액] {total_income - total_expense:,.0f}원")

        if categories:
            lines.append(f"\n[카테고리별 지출]")
            for cat, amount in list(categories.items())[:8]:
                lines.append(f"  - {cat}: {amount:,.0f}원")

        return {
            "report_text": "\n".join(lines),
            "month": now.strftime("%Y-%m"),
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": total_income - total_expense,
            "expense_by_category": categories,
        }
