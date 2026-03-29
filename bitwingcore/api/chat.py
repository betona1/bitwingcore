"""채팅 API — 핵심 명령 처리 엔드포인트."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from bitwingcore.ai_engine.intent_parser import parse_intent
from bitwingcore.ai_engine.response_builder import build_simple_response
from bitwingcore.api.schemas import ChatRequest
from bitwingcore.auth import verify_api_key
from bitwingcore.database import get_db
from bitwingcore.managers.dispatcher import dispatch
from bitwingcore.utils.response import success_response

router = APIRouter(tags=["chat"])


@router.post("/chat")
async def chat(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> dict:
    """자연어 명령 처리.

    1. 의도 분석 (규칙 → Claude 폴백)
    2. 매니저 디스패치
    3. 응답 생성
    """
    # 의도 분석
    parsed = await parse_intent(req.message)
    intent = parsed["intent"]
    manager_name = parsed["manager"]
    params = parsed["params"]

    # 매니저에게 디스패치
    result = await dispatch(manager_name, intent, params, db)

    # 응답 생성
    if "error" in result:
        return success_response(
            data=result,
            message=result["error"],
        )

    response_text = build_simple_response(intent, result)

    return success_response(
        data={
            "response": response_text,
            "intent": intent,
            "manager": manager_name,
            "method": parsed.get("method", "unknown"),
            "result": result,
        },
        message=response_text,
    )
