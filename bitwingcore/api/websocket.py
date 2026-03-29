"""WebSocket API — 실시간 통신 엔드포인트."""

import uuid

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from loguru import logger

from bitwingcore.config import get_settings
from bitwingcore.utils.ws_manager import ws_manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket 연결 핸들러.

    클라이언트 인증 후 양방향 실시간 통신을 처리한다.
    메시지 형식: {"type": "...", "data": {...}}
    """
    # 인증: 쿼리 파라미터 또는 헤더에서 API 키 확인
    settings = get_settings()
    api_key = websocket.query_params.get("api_key", "")

    if settings.API_KEY and api_key != settings.API_KEY:
        await websocket.close(code=4001, reason="인증 실패")
        return

    client_id = websocket.query_params.get("client_id", uuid.uuid4().hex[:8])
    await ws_manager.connect(client_id, websocket)

    try:
        # 연결 확인 메시지
        await ws_manager.send_to(client_id, {
            "type": "connected",
            "data": {
                "client_id": client_id,
                "message": "Bitwing Core에 연결되었습니다.",
            },
        })

        while True:
            raw = await websocket.receive_text()
            import json
            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                await ws_manager.send_to(client_id, {
                    "type": "error",
                    "data": {"message": "잘못된 JSON 형식입니다."},
                })
                continue

            msg_type = message.get("type", "")
            msg_data = message.get("data", {})

            # 메시지 타입별 처리
            if msg_type == "ping":
                await ws_manager.send_to(client_id, {"type": "pong", "data": {}})

            elif msg_type == "chat":
                # 채팅 메시지 처리 (DB 세션 필요 시 별도 처리)
                await ws_manager.send_to(client_id, {
                    "type": "chat_received",
                    "data": {"message": msg_data.get("message", ""), "status": "received"},
                })

            elif msg_type == "status":
                await ws_manager.send_to(client_id, {
                    "type": "status",
                    "data": {
                        "active_clients": ws_manager.active_count,
                        "client_id": client_id,
                    },
                })

            else:
                await ws_manager.send_to(client_id, {
                    "type": "unknown",
                    "data": {"message": f"알 수 없는 메시지 타입: {msg_type}"},
                })

    except WebSocketDisconnect:
        ws_manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket 오류 ({client_id}): {e}")
        ws_manager.disconnect(client_id)
