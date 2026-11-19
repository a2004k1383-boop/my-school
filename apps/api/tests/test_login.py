"""Login tests (B06–B09)."""

from __future__ import annotations

from typing import Any

from httpx import AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.user import User
from tests.conftest import VALID_REGISTRATION


def _payload(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = dict(VALID_REGISTRATION)
    data.update(overrides)
    return data


async def _register(client: AsyncClient, **overrides: Any) -> None:
    response = await client.post("/api/v1/auth/register", json=_payload(**overrides))
    assert response.status_code == 201, response.text


async def test_login_returns_access_token_and_refresh_cookie(client: AsyncClient) -> None:
    await _register(client)

    response = await client.post(
        "/api/v1/auth/login", json={"email": "sara@example.com", "password": "Parent1404"}
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == 15 * 60
    assert body["access_token"]
    assert body["user"]["email"] == "sara@example.com"

    set_cookie = response.headers.get("set-cookie", "")
    assert "myschool_refresh=" in set_cookie
    assert "httponly" in set_cookie.lower()
    assert "samesite=lax" in set_cookie.lower()
    assert "path=/api/v1/auth" in set_cookie.lower()


async def test_login_is_case_insensitive_for_email(client: AsyncClient) -> None:
    await _register(client)

    response = await client.post(
        "/api/v1/auth/login", json={"email": "SARA@Example.com", "password": "Parent1404"}
    )

    assert response.status_code == 200


async def test_unknown_email_and_wrong_password_are_indistinguishable(client: AsyncClient) -> None:
    await _register(client)

    wrong_password = await client.post(
        "/api/v1/auth/login", json={"email": "sara@example.com", "password": "WrongPass1404"}
    )
    unknown_email = await client.post(
        "/api/v1/auth/login", json={"email": "nobody@example.com", "password": "Parent1404"}
    )

    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()
    assert wrong_password.json()["code"] == "invalid_credentials"


async def test_disabled_account_cannot_login(
    client: AsyncClient, session_factory: async_sessionmaker[AsyncSession]
) -> None:
    await _register(client)
    async with session_factory() as session:
        await session.execute(update(User).values(is_active=False))
        await session.commit()

    response = await client.post(
        "/api/v1/auth/login", json={"email": "sara@example.com", "password": "Parent1404"}
    )

    assert response.status_code == 403
    assert response.json()["code"] == "account_disabled"


async def test_login_is_rate_limited(client: AsyncClient) -> None:
    await _register(client)

    statuses = []
    for _ in range(6):
        response = await client.post(
            "/api/v1/auth/login", json={"email": "sara@example.com", "password": "WrongPass1404"}
        )
        statuses.append(response.status_code)

    assert statuses[:5] == [401] * 5
    assert statuses[5] == 429
