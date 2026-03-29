"""Fernet 암/복호화 유틸리티."""

from cryptography.fernet import Fernet
from loguru import logger

from bitwingcore.config import get_settings

_fernet: Fernet | None = None


def _get_fernet() -> Fernet:
    """Fernet 인스턴스 (싱글톤)."""
    global _fernet
    if _fernet is None:
        settings = get_settings()
        key = settings.JWT_SECRET[:43] + "="
        _fernet = Fernet(Fernet.generate_key())
    return _fernet


def encrypt_value(raw: str) -> str:
    """문자열 암호화.

    Args:
        raw: 암호화할 원본 문자열

    Returns:
        암호화된 문자열 (base64)
    """
    f = _get_fernet()
    return f.encrypt(raw.encode()).decode()


def decrypt_value(enc: str) -> str:
    """문자열 복호화.

    Args:
        enc: 암호화된 문자열

    Returns:
        복호화된 원본 문자열
    """
    f = _get_fernet()
    try:
        return f.decrypt(enc.encode()).decode()
    except Exception as e:
        logger.error("복호화 실패: {}", e)
        raise ValueError("복호화에 실패했습니다.") from e
