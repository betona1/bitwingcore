"""텔레그램 알림 유틸리티."""

import httpx
from loguru import logger

from bitwingcore.config import get_settings


async def send_telegram(message: str, parse_mode: str | None = None) -> bool:
    """기본 채팅으로 텔레그램 메시지 전송.

    Args:
        message: 전송할 메시지
        parse_mode: 파싱 모드 ("HTML" 또는 "Markdown")

    Returns:
        전송 성공 여부
    """
    settings = get_settings()
    return await send_telegram_to(
        chat_id=settings.TELEGRAM_CHAT_ID,
        message=message,
        token=settings.TELEGRAM_BOT_TOKEN,
        parse_mode=parse_mode,
    )


async def send_telegram_to(
    chat_id: str,
    message: str,
    token: str | None = None,
    parse_mode: str | None = None,
) -> bool:
    """특정 채팅으로 텔레그램 메시지 전송.

    Args:
        chat_id: 텔레그램 채팅 ID
        message: 전송할 메시지
        token: 봇 토큰 (없으면 설정에서 가져옴)
        parse_mode: 파싱 모드

    Returns:
        전송 성공 여부
    """
    if not token:
        token = get_settings().TELEGRAM_BOT_TOKEN

    if not token or not chat_id:
        logger.warning("텔레그램 봇 토큰 또는 채팅 ID가 설정되지 않았습니다.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload: dict = {"chat_id": chat_id, "text": message}
    if parse_mode:
        payload["parse_mode"] = parse_mode

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                logger.debug("텔레그램 전송 성공: chat_id={}", chat_id)
                return True
            logger.error("텔레그램 전송 실패: {} {}", resp.status_code, resp.text)
            return False
    except httpx.HTTPError as e:
        logger.error("텔레그램 전송 오류: {}", e)
        return False
