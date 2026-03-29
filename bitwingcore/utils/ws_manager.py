"""WebSocket 연결 관리자."""

import json
from typing import Any

from fastapi import WebSocket
from loguru import logger


class ConnectionManager:
    """WebSocket 연결 관리 — 클라이언트 연결/해제/브로드캐스트."""

    def __init__(self) -> None:
        """연결 매니저 초기화."""
        self._connections: dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket) -> None:
        """클라이언트 연결 수락.

        Args:
            client_id: 클라이언트 식별자
            websocket: WebSocket 연결
        """
        await websocket.accept()
        self._connections[client_id] = websocket
        logger.info(f"WebSocket 연결: {client_id} (총 {len(self._connections)}명)")

    def disconnect(self, client_id: str) -> None:
        """클라이언트 연결 해제.

        Args:
            client_id: 클라이언트 식별자
        """
        self._connections.pop(client_id, None)
        logger.info(f"WebSocket 해제: {client_id} (총 {len(self._connections)}명)")

    async def send_to(self, client_id: str, data: dict[str, Any]) -> None:
        """특정 클라이언트에 메시지 전송.

        Args:
            client_id: 대상 클라이언트
            data: 전송할 데이터
        """
        ws = self._connections.get(client_id)
        if ws:
            try:
                await ws.send_text(json.dumps(data, ensure_ascii=False, default=str))
            except Exception as e:
                logger.warning(f"메시지 전송 실패 ({client_id}): {e}")
                self.disconnect(client_id)

    async def broadcast(self, data: dict[str, Any]) -> None:
        """연결된 모든 클라이언트에 브로드캐스트.

        Args:
            data: 전송할 데이터
        """
        message = json.dumps(data, ensure_ascii=False, default=str)
        disconnected = []

        for client_id, ws in self._connections.items():
            try:
                await ws.send_text(message)
            except Exception:
                disconnected.append(client_id)

        for client_id in disconnected:
            self.disconnect(client_id)

    @property
    def active_count(self) -> int:
        """현재 활성 연결 수."""
        return len(self._connections)

    @property
    def active_clients(self) -> list[str]:
        """현재 연결된 클라이언트 ID 목록."""
        return list(self._connections.keys())


# 글로벌 싱글톤
ws_manager = ConnectionManager()
