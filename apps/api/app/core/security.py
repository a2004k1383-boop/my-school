"""Password hashing, JWT access tokens and opaque refresh tokens."""

from __future__ import annotations

import hashlib
import hmac
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings

_password_hash = PasswordHash.recommended()

# A real Argon2id hash of an unguessable value, used to equalize timing when the
# email is unknown so login cannot be used to enumerate accounts.
_DUMMY_HASH = _password_hash.hash(secrets.token_urlsafe(32))

_REFRESH_TOKEN_BYTES = 32


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _password_hash.verify(password, password_hash)


def verify_dummy_password(password: str) -> None:
    """Burn the same amount of work as a real verification (timing equalizer)."""
    try:
        _password_hash.verify(password, _DUMMY_HASH)
    except Exception:  # noqa: BLE001 - timing equalizer must never raise
        pass


def invite_code_matches(candidate: str | None) -> bool:
    """Constant-time comparison against the configured teacher invite code."""
    if not candidate:
        return False
    expected = get_settings().teacher_invite_code
    if not expected:
        return False
    return hmac.compare_digest(candidate.strip().encode(), expected.encode())


def create_access_token(user_id: uuid.UUID, role: str) -> tuple[str, int]:
    settings = get_settings()
    expires_in = settings.access_token_ttl_minutes * 60
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "jti": str(uuid.uuid4()),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_in)).timestamp()),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, expires_in


class TokenError(Exception):
    """Raised when an access token is missing, expired or malformed."""

    def __init__(self, code: str = "invalid_token") -> None:
        super().__init__(code)
        self.code = code


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["exp", "sub", "type"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise TokenError("token_expired") from exc
    except jwt.PyJWTError as exc:
        raise TokenError("invalid_token") from exc

    if payload.get("type") != "access":
        raise TokenError("invalid_token")
    return payload


def new_refresh_token() -> tuple[str, str]:
    """Return ``(raw_token, sha256_hash)``; only the hash is persisted."""
    raw = secrets.token_urlsafe(_REFRESH_TOKEN_BYTES)
    return raw, hash_refresh_token(raw)


def hash_refresh_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()
