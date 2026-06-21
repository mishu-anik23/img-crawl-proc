from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_token(subject: str | UUID, expires_delta: timedelta, token_type: str) -> str:
    expire = datetime.now(UTC) + expires_delta
    payload: dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "type": token_type,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_access_token(subject: str | UUID) -> str:
    return create_token(
        subject,
        timedelta(minutes=settings.access_token_expire_minutes),
        "access",
    )


def create_refresh_token(subject: str | UUID) -> str:
    return create_token(
        subject,
        timedelta(days=settings.refresh_token_expire_days),
        "refresh",
    )


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])


def verify_token_type(payload: dict[str, Any], expected_type: str) -> str:
    token_type = payload.get("type")
    if token_type != expected_type:
        raise JWTError("Invalid token type")
    subject = payload.get("sub")
    if not subject:
        raise JWTError("Missing subject")
    return str(subject)
