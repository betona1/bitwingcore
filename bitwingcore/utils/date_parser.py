"""한국어 날짜/시간 파서 유틸리티."""

import re
from datetime import date, datetime, timedelta


def parse_korean_date(text: str) -> tuple[datetime, datetime]:
    """한국어 날짜 표현을 datetime 범위로 변환.

    Args:
        text: 한국어 날짜 표현 ("오늘", "내일", "이번주", "이번달" 등)

    Returns:
        (시작 datetime, 종료 datetime) 튜플
    """
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=0)

    # 오늘
    if re.search(r"오늘", text):
        return today_start, today_end

    # 어제
    if re.search(r"어제", text):
        yesterday = today_start - timedelta(days=1)
        return yesterday, yesterday.replace(hour=23, minute=59, second=59)

    # 내일
    if re.search(r"내일", text):
        tomorrow = today_start + timedelta(days=1)
        return tomorrow, tomorrow.replace(hour=23, minute=59, second=59)

    # 모레 / 내일모레
    if re.search(r"모레|내일\s*모레", text):
        day_after = today_start + timedelta(days=2)
        return day_after, day_after.replace(hour=23, minute=59, second=59)

    # 이번주
    if re.search(r"이번\s*주", text):
        monday = today_start - timedelta(days=now.weekday())
        sunday = monday + timedelta(days=6)
        return monday, sunday.replace(hour=23, minute=59, second=59)

    # 다음주
    if re.search(r"다음\s*주", text):
        next_monday = today_start + timedelta(days=7 - now.weekday())
        next_sunday = next_monday + timedelta(days=6)
        return next_monday, next_sunday.replace(hour=23, minute=59, second=59)

    # 지난주
    if re.search(r"지난\s*주", text):
        last_monday = today_start - timedelta(days=now.weekday() + 7)
        last_sunday = last_monday + timedelta(days=6)
        return last_monday, last_sunday.replace(hour=23, minute=59, second=59)

    # 이번달
    if re.search(r"이번\s*달", text):
        month_start = today_start.replace(day=1)
        if now.month == 12:
            month_end = today_start.replace(year=now.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = today_start.replace(month=now.month + 1, day=1) - timedelta(days=1)
        return month_start, month_end.replace(hour=23, minute=59, second=59)

    # 다음달
    if re.search(r"다음\s*달", text):
        if now.month == 12:
            next_month_start = today_start.replace(year=now.year + 1, month=1, day=1)
        else:
            next_month_start = today_start.replace(month=now.month + 1, day=1)
        if next_month_start.month == 12:
            next_month_end = next_month_start.replace(year=next_month_start.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            next_month_end = next_month_start.replace(month=next_month_start.month + 1, day=1) - timedelta(days=1)
        return next_month_start, next_month_end.replace(hour=23, minute=59, second=59)

    # 지난달
    if re.search(r"지난\s*달", text):
        if now.month == 1:
            last_month_start = today_start.replace(year=now.year - 1, month=12, day=1)
        else:
            last_month_start = today_start.replace(month=now.month - 1, day=1)
        last_month_end = today_start.replace(day=1) - timedelta(days=1)
        return last_month_start, last_month_end.replace(hour=23, minute=59, second=59)

    # N월 N일
    match = re.search(r"(\d{1,2})\s*월\s*(\d{1,2})\s*일", text)
    if match:
        month = int(match.group(1))
        day = int(match.group(2))
        target = today_start.replace(month=month, day=day)
        return target, target.replace(hour=23, minute=59, second=59)

    # 요일 (다음주 월요일 등)
    weekday_map = {"월": 0, "화": 1, "수": 2, "목": 3, "금": 4, "토": 5, "일": 6}
    match = re.search(r"다음\s*주?\s*(월|화|수|목|금|토|일)\s*요?일?", text)
    if match:
        target_weekday = weekday_map[match.group(1)]
        days_ahead = target_weekday - now.weekday() + 7
        target = today_start + timedelta(days=days_ahead)
        return target, target.replace(hour=23, minute=59, second=59)

    # 기본: 오늘
    return today_start, today_end


def parse_korean_time(text: str) -> datetime | None:
    """한국어 시간 표현을 datetime으로 변환.

    Args:
        text: "오후 3시", "14시 30분" 등

    Returns:
        datetime 또는 None
    """
    now = datetime.now()

    # 오후/오전 N시 (N분)
    match = re.search(r"(오전|오후)\s*(\d{1,2})\s*시\s*(\d{1,2})?\s*분?", text)
    if match:
        period = match.group(1)
        hour = int(match.group(2))
        minute = int(match.group(3)) if match.group(3) else 0
        if period == "오후" and hour < 12:
            hour += 12
        elif period == "오전" and hour == 12:
            hour = 0
        return now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # N시 (N분) — 24시간 형식
    match = re.search(r"(\d{1,2})\s*시\s*(\d{1,2})?\s*분?", text)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        return now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    return None


def parse_korean_amount(text: str) -> int | None:
    """한국어 금액 표현을 정수로 변환.

    Args:
        text: "12,000원", "만이천원", "5만원" 등

    Returns:
        금액 정수 또는 None
    """
    # 숫자 + 원
    match = re.search(r"([\d,]+)\s*원", text)
    if match:
        return int(match.group(1).replace(",", ""))

    # 한국어 숫자
    korean_nums = {"만": 10000, "천": 1000, "백": 100}
    digit_map = {
        "일": 1, "이": 2, "삼": 3, "사": 4, "오": 5,
        "육": 6, "칠": 7, "팔": 8, "구": 9,
    }

    match = re.search(r"(\d+)\s*만\s*(\d+)?\s*원?", text)
    if match:
        result = int(match.group(1)) * 10000
        if match.group(2):
            result += int(match.group(2))
        return result

    return None
