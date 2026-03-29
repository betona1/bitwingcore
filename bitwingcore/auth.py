"""Bitwing Core 인증 모듈."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from bitwingcore.config import get_settings

security = HTTPBearer()


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """API Key 검증 의존성.

    Returns:
        검증된 API Key 문자열.

    Raises:
        HTTPException: 인증 실패 시.
    """
    settings = get_settings()
    if not settings.API_KEY:
        return credentials.credentials

    if credentials.credentials != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 API 키입니다.",
        )
    return credentials.credentials
