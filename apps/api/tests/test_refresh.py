"""Refresh rotation, reuse detection and cookie security (B10–B12)."""

from __future__ import annotations

import re

from httpx import AsyncClient, Response

from tests.conftest import VALID_REGISTRATION

CSRF = {"X-Requested-With": "XMLHttpRequest"}


def _cookie(response: Response) -> str:
    header = response.headers.get("set-cookie", "")
    match = re.search(r"myschool_refresh=([^;]+)", header)
    assert match is not None, header
    return match.group(1)


async def _login(client: AsyncClient) -> Response:
    await client.post("/api/v1/auth/register", json=dict(VALID_REGISTRATION))
    return await client.post(
        "/api/v1/auth/login", json={"email": "sara@example.com", "password": "Parent1404"}
    )


async def test_refresh_rotates_the_token(client: AsyncClient) -> None:
    login = await _login(client)
    old_token = _cookie(login)

    response = await client.post(
        "/api/v1/auth/refresh",
        headers={**CSRF, "Cookie": f"myschool_refresh={old_token}"},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["access_token"]
    assert body["expires_in"] == 15 * 60
    assert _cookie(response) != old_token


async def test_reused_refresh_token_revokes_the_family(client: AsyncClient) -> None:
    login = await _login(client)
    old_token = _cookie(login)

    rotated = await client.post(
        "/api/v1/auth/refresh",
        headers={**CSRF, "Cookie": f"myschool_refresh={old_token}"},
    )
    assert rotated.status_code == 200
    new_token = _cookie(rotated)

    replay = await client.post(
        "/api/v1/auth/refresh",
        headers={**CSRF, "Cookie": f"myschool_refresh={old_token}"},
    )
    assert replay.status_code == 401
    assert replay.json()["code"] == "refresh_reused"

    # The replacement token belongs to the revoked family and must fail too.
    after = await client.post(
        "/api/v1/auth/refresh",
        headers={**CSRF, "Cookie": f"myschool_refresh={new_token}"},
    )
    assert after.status_code == 401


async def test_refresh_requires_csrf_header(client: AsyncClient) -> None:
    login = await _login(client)
    token = _cookie(login)

    response = await client.post(
        "/api/v1/auth/refresh", headers={"Cookie": f"myschool_refresh={token}"}
    )

    assert response.status_code == 403
    assert response.json()["code"] == "csrf_failed"


async def test_refresh_without_cookie_is_rejected(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/refresh", headers=CSRF)

    assert response.status_code == 401
    assert response.json()["code"] == "refresh_expired"


async def test_logout_revokes_the_token(client: AsyncClient) -> None:
    login = await _login(client)
    token = _cookie(login)

    logout = await client.post(
        "/api/v1/auth/logout",
        headers={**CSRF, "Cookie": f"myschool_refresh={token}"},
    )
    assert logout.status_code == 204

    after = await client.post(
        "/api/v1/auth/refresh",
        headers={**CSRF, "Cookie": f"myschool_refresh={token}"},
    )
    assert after.status_code == 401
