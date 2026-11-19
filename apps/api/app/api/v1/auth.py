"""HTTP endpoints for the identity module."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Header, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.rate_limit import limiter
from app.core.security import TokenError, create_access_token, decode_access_token
from app.db.session import get_session
from app.schemas.auth import (
    AccessTokenResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserPublic,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])
bearer = HTTPBearer(auto_error=False)

COOKIE_PATH = "/api/v1/auth"
COOKIE_NAME = get_settings().refresh_cookie_name


def require_csrf_header(
    x_requested_with: Annotated[str | None, Header(alias="X-Requested-With")] = None,
) -> None:
    if x_requested_with != "XMLHttpRequest":
        raise AppError("csrf_failed", 403, "CSRF check failed", "درخواست نامعتبر است.")


def _set_refresh_cookie(response: Response, raw_token: str, max_age: int) -> None:
    settings = get_settings()
    response.set_cookie(
        key=COOKIE_NAME,
        value=raw_token,
        max_age=max_age,
        httponly=True,
        samesite="lax",
        secure=settings.is_production,
        path=COOKIE_PATH,
    )


def _client_ip(request: Request) -> str | None:
    if request.client is None:
        return None
    return request.client.host


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create a parent, student or invited teacher account",
    responses={409: {"description": "Email already registered"}},
)
@limiter.limit("3/minute")
async def register(
    request: Request,
    payload: RegisterRequest,
    session: AsyncSession = Depends(get_session),
) -> UserPublic:
    user = await auth_service.register_user(session, payload)
    return UserPublic.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Exchange credentials for an access token and a refresh cookie",
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    payload: LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    user = await auth_service.authenticate(session, payload.email, payload.password)
    raw_refresh, max_age = await auth_service.issue_refresh_token(
        session,
        user,
        remember_me=payload.remember_me,
        user_agent=request.headers.get("user-agent"),
        ip=_client_ip(request),
    )
    _set_refresh_cookie(response, raw_refresh, max_age)
    access_token, expires_in = create_access_token(user.id, user.role.value)
    return TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
        user=UserPublic.model_validate(user),
    )


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    summary="Rotate the refresh token and issue a new access token",
)
async def refresh(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
    refresh_token: str | None = Cookie(default=None, alias=COOKIE_NAME),
    _: None = Depends(require_csrf_header),
) -> AccessTokenResponse:
    if not refresh_token:
        raise AppError(
            "refresh_expired", 401, "Refresh expired", "نشست شما منقضی شده است. دوباره وارد شوید."
        )
    new_raw, access_token, expires_in, max_age, _user = await auth_service.rotate_refresh_token(
        session,
        refresh_token,
        user_agent=request.headers.get("user-agent"),
        ip=_client_ip(request),
    )
    _set_refresh_cookie(response, new_raw, max_age)
    return AccessTokenResponse(access_token=access_token, expires_in=expires_in)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="End the session")
async def logout(
    response: Response,
    session: AsyncSession = Depends(get_session),
    refresh_token: str | None = Cookie(default=None, alias=COOKIE_NAME),
    _: None = Depends(require_csrf_header),
) -> Response:
    if refresh_token:
        await auth_service.revoke_session_by_token(session, refresh_token)
    response.delete_cookie(key=COOKIE_NAME, path=COOKIE_PATH)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/me", response_model=UserPublic, summary="Current authenticated user")
async def me(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    session: AsyncSession = Depends(get_session),
) -> UserPublic:
    if credentials is None:
        raise AppError("unauthorized", 401, "Unauthorized", "برای دسترسی باید وارد شوید.")
    try:
        payload = decode_access_token(credentials.credentials)
    except TokenError as exc:
        raise AppError(exc.code, 401, "Unauthorized", "نشست شما منقضی شده است.") from exc

    try:
        user_id = uuid.UUID(str(payload["sub"]))
    except (KeyError, ValueError) as exc:
        raise AppError("invalid_token", 401, "Unauthorized", "توکن نامعتبر است.") from exc

    user = await auth_service.get_user_by_id(session, user_id)
    if user is None:
        raise AppError("invalid_token", 401, "Unauthorized", "توکن نامعتبر است.")
    if not user.is_active:
        raise AppError("account_disabled", 403, "Account disabled", "این حساب غیرفعال شده است.")
    return UserPublic.model_validate(user)
