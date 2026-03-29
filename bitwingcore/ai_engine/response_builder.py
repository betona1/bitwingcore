"""구조화된 결과를 한국어 자연어 응답으로 변환."""

from datetime import date, datetime
from typing import Any

from loguru import logger

from bitwingcore.ai_engine.claude_client import get_claude_client


def build_simple_response(intent: str, data: dict[str, Any]) -> str:
    """규칙 기반 간단 응답 생성.

    Args:
        intent: 의도 코드
        data: 처리 결과 데이터

    Returns:
        한국어 응답 문자열
    """
    domain, action = intent.split(".", 1) if "." in intent else (intent, "")

    # 일정
    if domain == "schedule":
        if action == "create":
            title = data.get("title", "")
            start = _format_datetime(data.get("start_at"))
            return f"일정 '{title}'을(를) {start}에 등록했습니다."
        if action == "list":
            items = data.get("items", [])
            if not items:
                return "등록된 일정이 없습니다."
            lines = [f"총 {len(items)}건의 일정:"]
            for i, item in enumerate(items[:10], 1):
                start = _format_datetime(item.get("start_at"))
                lines.append(f"  {i}. {item.get('title', '')} ({start})")
            return "\n".join(lines)
        if action == "delete":
            return f"일정을 삭제했습니다."
        if action == "update":
            return f"일정을 수정했습니다."

    # 할일
    if domain == "todo":
        if action == "create":
            return f"할일 '{data.get('title', '')}'을(를) 등록했습니다."
        if action == "list":
            items = data.get("items", [])
            if not items:
                return "등록된 할일이 없습니다."
            lines = [f"총 {len(items)}건의 할일:"]
            for i, item in enumerate(items[:10], 1):
                status = _status_emoji(item.get("status", ""))
                lines.append(f"  {i}. {status} {item.get('title', '')}")
            return "\n".join(lines)
        if action == "complete":
            return f"할일을 완료 처리했습니다."

    # 메모
    if domain == "memo":
        if action == "create":
            return f"메모를 저장했습니다."
        if action == "list":
            items = data.get("items", [])
            if not items:
                return "저장된 메모가 없습니다."
            lines = [f"총 {len(items)}건의 메모:"]
            for i, item in enumerate(items[:5], 1):
                content = (item.get("content", "") or "")[:50]
                lines.append(f"  {i}. {item.get('title', '무제')} — {content}")
            return "\n".join(lines)

    # 가계부
    if domain == "finance":
        if action == "add":
            return f"{data.get('type_display', '지출')} {data.get('amount', 0):,}원을 기록했습니다."
        if action == "summary":
            return _build_finance_summary(data)
        if action == "list":
            items = data.get("items", [])
            if not items:
                return "거래 내역이 없습니다."
            lines = [f"총 {len(items)}건의 거래:"]
            for i, item in enumerate(items[:10], 1):
                t = "수입" if item.get("type") == "income" else "지출"
                lines.append(f"  {i}. [{t}] {item.get('category', '')} {item.get('amount', 0):,}원")
            return "\n".join(lines)

    # 리포트
    if domain == "report":
        return data.get("report_text", "리포트를 생성했습니다.")

    # 이메일
    if domain == "email":
        if action == "list":
            items = data.get("items", [])
            if not items:
                return "확인할 이메일이 없습니다."
            lines = [f"총 {len(items)}건의 이메일:"]
            for i, item in enumerate(items[:5], 1):
                lines.append(f"  {i}. {item.get('sender', '')} — {item.get('subject', '제목없음')}")
            return "\n".join(lines)

    # 일반
    return data.get("message", "처리가 완료되었습니다.")


async def build_natural_response(
    intent: str,
    data: dict[str, Any],
    user_message: str = "",
) -> str:
    """Claude를 활용한 자연어 응답 생성.

    Args:
        intent: 의도 코드
        data: 처리 결과 데이터
        user_message: 원본 사용자 메시지

    Returns:
        자연스러운 한국어 응답
    """
    # 간단한 결과는 규칙 기반으로 처리
    simple = build_simple_response(intent, data)
    if not data.get("use_ai_response", False):
        return simple

    try:
        client = get_claude_client()
        prompt = f"""다음 처리 결과를 사용자에게 친근하게 보고하라. 비서 말투를 사용하라.

사용자 요청: {user_message}
처리 의도: {intent}
처리 결과: {simple}

간결하게 2~3문장으로 응답하라."""

        return await client.chat(
            prompt,
            system_prompt="너는 AI 비서 비트윙이다. 존댓말을 사용하고, 간결하게 보고한다.",
            max_tokens=256,
            temperature=0.5,
        )
    except Exception as e:
        logger.warning(f"자연어 응답 생성 실패, 기본 응답 사용: {e}")
        return simple


def _format_datetime(value: Any) -> str:
    """datetime/date/str을 한국어 문자열로 포맷."""
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y년 %m월 %d일 %H시 %M분")
    if isinstance(value, date):
        return value.strftime("%Y년 %m월 %d일")
    return str(value)


def _status_emoji(status: str) -> str:
    """상태 이모지 반환."""
    return {
        "pending": "[ ]",
        "in_progress": "[~]",
        "completed": "[v]",
        "cancelled": "[x]",
    }.get(status, "[ ]")


def _build_finance_summary(data: dict[str, Any]) -> str:
    """가계부 요약 응답 생성."""
    period = data.get("period", "")
    income = data.get("total_income", 0)
    expense = data.get("total_expense", 0)
    balance = income - expense

    lines = [f"{period} 가계부 요약:"]
    lines.append(f"  수입: {income:,.0f}원")
    lines.append(f"  지출: {expense:,.0f}원")
    lines.append(f"  잔액: {balance:,.0f}원")

    categories = data.get("expense_by_category", {})
    if categories:
        lines.append("  지출 카테고리:")
        for cat, amount in sorted(categories.items(), key=lambda x: -x[1])[:5]:
            lines.append(f"    - {cat}: {amount:,.0f}원")

    return "\n".join(lines)
