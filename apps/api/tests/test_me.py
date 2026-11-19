"""/auth/me tests (B14)."""

from __future__ import annotations

from httpx import AsyncClient, Response

from tests.conftest import VALID_REGISTRATION


async def _login(client: AsyncClient) -> Response:
    await client.post("/api/v1/auth/register", json=dict(VALID_REGISTRATION))
    return await client.post(
        "/api/v1/auth/login", json={"email": "sara@example.com", "password": "Parent1404"}
    )


async def test_me_returns_current_user(client: AsyncClient) -> None:
    login = await _login(client)
    token = login.json()["access_token"]

    response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "sara@example.com"
    assert body["role"] == "parent"
    assert "password_hash" not in body


async def test_me_rejects_invalid_token(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-token"})

    assert response.status_code == 401
    assert response.json()["code"] == "invalid_token"


async def test_me_requires_authentication(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json()["code"] == "unauthorized"
