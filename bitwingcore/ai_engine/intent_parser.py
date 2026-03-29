"""2단계 의도 분석기 — 규칙 기반 + Claude 폴백."""

import re
from typing import Any

from loguru import logger

from bitwingcore.ai_engine.claude_client import get_claude_client

# 규칙 기반 의도 매핑 테이블
RULE_PATTERNS: list[tuple[str, list[str], dict[str, str]]] = [
    # (intent, 키워드 패턴 리스트, 추가 파라미터 추출 힌트)
    # === 일정 ===
    ("schedule.create", [r"일정.*(?:등록|추가|잡아|넣어|만들어)"], {}),
    ("schedule.list", [r"일정.*(?:확인|보여|알려|목록|뭐)", r"오늘.*(?:일정|스케줄)"], {}),
    ("schedule.update", [r"일정.*(?:수정|변경|옮기|바꿔)"], {}),
    ("schedule.delete", [r"일정.*(?:삭제|취소|지워)"], {}),
    # === 할일 ===
    ("todo.create", [r"할\s*일.*(?:등록|추가|넣어|만들어)", r"(?:해야|해줘).*(?:할\s*일|todo)"], {}),
    ("todo.list", [r"할\s*일.*(?:확인|보여|알려|목록|뭐)", r"오늘.*할\s*일"], {}),
    ("todo.complete", [r"할\s*일.*(?:완료|끝|했)"], {}),
    ("todo.delete", [r"할\s*일.*(?:삭제|지워|취소)"], {}),
    # === 메모 ===
    ("memo.create", [r"메모.*(?:등록|추가|저장|남겨|적어)", r"(?:기록|적어).*(?:줘|줄래)"], {}),
    ("memo.list", [r"메모.*(?:확인|보여|검색|목록|찾아)"], {}),
    ("memo.search", [r"메모.*(?:검색|찾아)"], {}),
    ("memo.delete", [r"메모.*(?:삭제|지워)"], {}),
    # === 가계부 ===
    ("finance.add", [r"(?:가계부|지출|수입|비용).*(?:등록|추가|기록|넣어)", r"(?:\d+원|\d+,\d+원).*(?:썼|사용|결제)"], {}),
    ("finance.list", [r"(?:가계부|지출|수입|비용).*(?:확인|보여|목록|내역)", r"(?:이번\s*달|오늘).*(?:지출|수입|가계부)"], {}),
    ("finance.summary", [r"(?:가계부|지출|수입).*(?:요약|통계|합계|총액)"], {}),
    # === 이메일 ===
    ("email.list", [r"(?:이메일|메일).*(?:확인|보여|목록|읽지\s*않은)"], {}),
    ("email.summary", [r"(?:이메일|메일).*(?:요약|중요)"], {}),
    # === PC 관리 ===
    ("pc.status", [r"(?:PC|컴퓨터|사원).*(?:상태|확인|목록)"], {}),
    ("pc.command", [r"(?:PC|컴퓨터).*(?:실행|명령|원격)"], {}),
    # === 리포트 ===
    ("report.daily", [r"(?:일일|오늘|데일리).*(?:보고|리포트|보고서)"], {}),
    ("report.weekly", [r"(?:주간|이번\s*주|위클리).*(?:보고|리포트|보고서)"], {}),
    ("report.monthly", [r"(?:월간|이번\s*달|먼슬리).*(?:보고|리포트|보고서)"], {}),
    # === 파일 ===
    ("file.upload", [r"파일.*(?:업로드|올려|저장)"], {}),
    ("file.list", [r"파일.*(?:목록|확인|보여|검색)"], {}),
    # === 일반 대화 ===
    ("chat.general", [r"^(?:안녕|하이|헬로|고마워|감사|ㅎㅇ)"], {}),
]

# intent → 매니저 매핑
INTENT_MANAGER_MAP: dict[str, str] = {
    "schedule": "schedule_mgr",
    "todo": "task_mgr",
    "memo": "task_mgr",
    "finance": "finance_mgr",
    "email": "task_mgr",
    "pc": "it_mgr",
    "report": "report_mgr",
    "file": "task_mgr",
    "chat": "schedule_mgr",  # 일반 대화는 기본 매니저
}


def parse_by_rules(text: str) -> dict[str, Any] | None:
    """규칙 기반 의도 분석 (1단계).

    Args:
        text: 사용자 입력 텍스트

    Returns:
        {"intent": str, "manager": str, "params": {}} 또는 None
    """
    text_lower = text.strip().lower()

    for intent, patterns, _ in RULE_PATTERNS:
        for pattern in patterns:
            if re.search(pattern, text_lower):
                domain = intent.split(".")[0]
                manager = INTENT_MANAGER_MAP.get(domain, "schedule_mgr")
                logger.debug(f"규칙 매칭: '{text[:30]}...' → {intent} ({manager})")
                return {
                    "intent": intent,
                    "manager": manager,
                    "params": {"raw_text": text},
                    "method": "rule",
                }

    return None


async def parse_by_claude(text: str) -> dict[str, Any]:
    """Claude AI 의도 분석 (2단계 폴백).

    Args:
        text: 사용자 입력 텍스트

    Returns:
        {"intent": str, "manager": str, "params": {}}
    """
    client = get_claude_client()

    system_prompt = """너는 AI 비서 시스템의 의도 분석기다. 사용자 메시지를 분석하여 JSON으로 응답하라.

사용 가능한 intent:
- schedule.create / schedule.list / schedule.update / schedule.delete (일정)
- todo.create / todo.list / todo.complete / todo.delete (할일)
- memo.create / memo.list / memo.search / memo.delete (메모)
- finance.add / finance.list / finance.summary (가계부)
- email.list / email.summary (이메일)
- pc.status / pc.command (PC 관리)
- report.daily / report.weekly / report.monthly (리포트)
- file.upload / file.list (파일)
- chat.general (일반 대화)

매니저 코드: schedule_mgr, task_mgr, finance_mgr, it_mgr, report_mgr

응답 형식 (JSON만 출력):
{"intent": "...", "manager": "...", "params": {"title": "...", "date": "...", ...}}"""

    try:
        result = await client.parse_json(
            f"사용자 메시지: {text}",
            system_prompt=system_prompt,
        )
        result["method"] = "claude"
        result.setdefault("params", {})["raw_text"] = text
        logger.debug(f"Claude 분석: '{text[:30]}...' → {result.get('intent')}")
        return result

    except Exception as e:
        logger.warning(f"Claude 의도 분석 실패, 기본값 반환: {e}")
        return {
            "intent": "chat.general",
            "manager": "schedule_mgr",
            "params": {"raw_text": text},
            "method": "fallback",
        }


async def parse_intent(text: str) -> dict[str, Any]:
    """2단계 의도 분석 (규칙 → Claude 폴백).

    Args:
        text: 사용자 입력 텍스트

    Returns:
        {"intent": str, "manager": str, "params": dict, "method": str}
    """
    # 1단계: 규칙 기반
    result = parse_by_rules(text)
    if result:
        return result

    # 2단계: Claude AI
    return await parse_by_claude(text)
