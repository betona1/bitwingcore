"""Bitwing Core 통일 API 응답 헬퍼."""

from typing import Any

from fastapi import HTTPException


def success_response(
    data: Any = None,
    message: str = "성공",
) -> dict[str, Any]:
    """성공 응답 생성."""
    return {"success": True, "message": message, "data": data}


def error_response(
    message: str = "오류가 발생했습니다.",
    status_code: int = 400,
) -> HTTPException:
    """에러 응답 생성 (HTTPException 반환)."""
    raise HTTPException(
        status_code=status_code,
        detail={"success": False, "message": message, "data": None},
    )
