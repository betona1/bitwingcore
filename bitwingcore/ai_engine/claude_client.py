"""Anthropic Claude API 클라이언트 래퍼."""

from typing import Any

import anthropic
from loguru import logger

from bitwingcore.config import get_settings


class ClaudeClient:
    """Claude API 비동기 클라이언트."""

    def __init__(self) -> None:
        """클라이언트 초기화."""
        settings = get_settings()
        self._client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self._model = settings.CLAUDE_MODEL

    async def chat(
        self,
        message: str,
        system_prompt: str = "",
        max_tokens: int = 2048,
        temperature: float = 0.3,
    ) -> str:
        """Claude에게 단일 메시지를 보내고 응답 텍스트를 반환.

        Args:
            message: 사용자 메시지
            system_prompt: 시스템 프롬프트
            max_tokens: 최대 토큰 수
            temperature: 생성 온도

        Returns:
            Claude 응답 텍스트
        """
        try:
            kwargs: dict[str, Any] = {
                "model": self._model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": message}],
            }
            if system_prompt:
                kwargs["system"] = system_prompt

            response = await self._client.messages.create(**kwargs)
            return response.content[0].text

        except anthropic.APIError as e:
            logger.error(f"Claude API 오류: {e}")
            raise

    async def chat_with_history(
        self,
        messages: list[dict[str, str]],
        system_prompt: str = "",
        max_tokens: int = 2048,
        temperature: float = 0.3,
    ) -> str:
        """대화 히스토리와 함께 Claude에게 요청.

        Args:
            messages: [{"role": "user"|"assistant", "content": "..."}] 리스트
            system_prompt: 시스템 프롬프트
            max_tokens: 최대 토큰 수
            temperature: 생성 온도

        Returns:
            Claude 응답 텍스트
        """
        try:
            kwargs: dict[str, Any] = {
                "model": self._model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages,
            }
            if system_prompt:
                kwargs["system"] = system_prompt

            response = await self._client.messages.create(**kwargs)
            return response.content[0].text

        except anthropic.APIError as e:
            logger.error(f"Claude API 오류: {e}")
            raise

    async def parse_json(
        self,
        message: str,
        system_prompt: str = "",
        max_tokens: int = 1024,
    ) -> dict[str, Any]:
        """Claude에게 JSON 형식 응답을 요청.

        Args:
            message: 사용자 메시지
            system_prompt: 시스템 프롬프트
            max_tokens: 최대 토큰 수

        Returns:
            파싱된 JSON 딕셔너리
        """
        import json

        prompt = f"{message}\n\n반드시 JSON 형식으로만 응답하세요. 다른 텍스트 없이 JSON만 출력하세요."
        raw = await self.chat(prompt, system_prompt=system_prompt, max_tokens=max_tokens, temperature=0.1)

        # JSON 블록 추출
        raw = raw.strip()
        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:-1])

        return json.loads(raw)


# 싱글톤
_client: ClaudeClient | None = None


def get_claude_client() -> ClaudeClient:
    """Claude 클라이언트 싱글톤 반환."""
    global _client
    if _client is None:
        _client = ClaudeClient()
    return _client
