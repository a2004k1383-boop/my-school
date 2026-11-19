"""Identity use cases: registration, login, refresh rotation, logout."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.security import (
    create_access_token,
    hash_password,
    hash_refresh_token,
    invite_code_matches,
    new_refresh_token,
    verify_dummy_password,
    verify_password,
)
from app.models.audit_log import AuditLog
from app.models.refresh_token import RefreshToken
from app.models.user import Role, User, utcnow
from app.schemas.auth import RegisterRequest

INVALID_CREDENTIALS_DETAIL = "ایمیل یا رمز عبور نادرست است."


def _aware(value: datetime) -> datetime:
    """SQLite returns naive datetimes; treat stored values as UTC."""
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


async def _get_user_by_email(session: AsyncSession, email: str) -> User | None:
    normalized = email.strip().lower()
    return await session.scalar(select(User).where(User.email == normalized))


async def register_user(session: AsyncSession, payload: RegisterRequest) -> User:
    email = payload.email.strip().lower()
    existing = await session.scalar(select(User).where(User.email == email))
    if existing is not None:
        raise AppError(
            "email_already_registered",
            409,
            "Email already registered",
            "این ایمیل قبلاً ثبت شده است.",
        )

    if payload.role is Role.teacher and not invite_code_matches(payload.invite_code):
        raise AppError(
            "invitation_required",
            403,
            "Invitation required",
            "کد دعوت معلم معتبر نیست.",
        )

    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        is_active=True,
    )
    session.add(user)
    try:
        await session.flush()
    except IntegrityError as exc:  # concurrent registration on the same email
        await session.rollback()
        raise AppError(
            "email_already_registered",
            409,
            "Email already registered",
            "این ایمیل قبلاً ثبت شده است.",
        ) from exc

    if user.role is Role.teacher:
        session.add(
            AuditLog(
                actor_id=user.id,
                action="teacher.registered",
                target_type="user",
                target_id=str(user.id),
                extra={"role": user.role.value},
            )
        )

    await session.commit()
    await session.refresh(user)
    return user


async def authenticate(session: AsyncSession, email: str, password: str) -> User:
    user = await _get_user_by_email(session, email)
    if user is None:
        verify_dummy_password(password)
        raise AppError(
            "invalid_credentials", 401, "Invalid credentials", INVALID_CREDENTIALS_DETAIL
        )

    if not verify_password(password, user.password_hash):
        raise AppError(
            "invalid_credentials", 401, "Invalid credentials", INVALID_CREDENTIALS_DETAIL
        )

    if not user.is_active:
        raise AppError("account_disabled", 403, "Account disabled", "این حساب غیرفعال شده است.")

    user.last_login_at = utcnow()
    await session.commit()
    await session.refresh(user)
    return user


async def issue_refresh_token(
    session: AsyncSession,
    user: User,
    *,
    remember_me: bool,
    user_agent: str | None,
    ip: str | None,
) -> tuple[str, int]:
    """Create a refresh-token family for a new session and return (raw, max_age)."""
    settings = get_settings()
    days = (
        settings.refresh_token_remember_ttl_days if remember_me else settings.refresh_token_ttl_days
    )
    raw, digest = new_refresh_token()
    session.add(
        RefreshToken(
            user_id=user.id,
            token_hash=digest,
            family_id=uuid.uuid4(),
            expires_at=datetime.now(UTC) + timedelta(days=days),
            user_agent=(user_agent or "")[:255] or None,
            ip=(ip or "")[:45] or None,
        )
    )
    await session.commit()
    return raw, days * 24 * 60 * 60


async def rotate_refresh_token(
    session: AsyncSession,
    raw_token: str,
    *,
    user_agent: str | None,
    ip: str | None,
) -> tuple[str, str, int, int, User]:
    """Validate and rotate a refresh token.

    Returns ``(raw_token, access_token, access_expires_in, cookie_max_age, user)``.
    """
    row = await session.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(raw_token))
    )
    if row is None:
        raise AppError(
            "refresh_expired", 401, "Refresh expired", "نشست شما منقضی شده است. دوباره وارد شوید."
        )

    if row.revoked_at is not None:
        await revoke_family(session, row.family_id)
        raise AppError(
            "refresh_reused",
            401,
            "Refresh token reused",
            "نشست شما به دلایل امنیتی بسته شد. دوباره وارد شوید.",
        )

    if _aware(row.expires_at) <= datetime.now(UTC):
        raise AppError(
            "refresh_expired", 401, "Refresh expired", "نشست شما منقضی شده است. دوباره وارد شوید."
        )

    user = await session.get(User, row.user_id)
    if user is None or not user.is_active:
        raise AppError("account_disabled", 403, "Account disabled", "این حساب غیرفعال شده است.")

    now = datetime.now(UTC)
    new_expiry = _aware(row.expires_at)
    raw, digest = new_refresh_token()
    replacement = RefreshToken(
        user_id=user.id,
        token_hash=digest,
        family_id=row.family_id,
        expires_at=new_expiry,
        user_agent=(user_agent or "")[:255] or None,
        ip=(ip or "")[:45] or None,
    )
    session.add(replacement)
    await session.flush()
    row.revoked_at = utcnow()
    row.replaced_by = replacement.id
    await session.commit()

    access_token, expires_in = create_access_token(user.id, user.role.value)
    max_age = max(0, int((new_expiry - now).total_seconds()))
    return raw, access_token, expires_in, max_age, user


async def revoke_family(session: AsyncSession, family_id: uuid.UUID) -> None:
    await session.execute(
        update(RefreshToken)
        .where(RefreshToken.family_id == family_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=utcnow())
    )
    await session.commit()


async def revoke_session_by_token(session: AsyncSession, raw_token: str) -> None:
    """Logout: revoke the whole family that owns this token, if it exists."""
    row = await session.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(raw_token))
    )
    if row is not None:
        await revoke_family(session, row.family_id)


async def get_user_by_id(session: AsyncSession, user_id: uuid.UUID) -> User | None:
    return await session.get(User, user_id)
