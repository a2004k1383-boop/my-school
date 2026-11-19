"""Registration tests (B01–B05)."""

from __future__ import annotations

from typing import Any

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.audit_log import AuditLog
from app.models.user import User
from tests.conftest import VALID_REGISTRATION


def _payload(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = dict(VALID_REGISTRATION)
    data.update(overrides)
    return data


async def test_register_parent_creates_user(
    client: AsyncClient, session_factory: async_sessionmaker[AsyncSession]
) -> None:
    response = await client.post("/api/v1/auth/register", json=_payload())

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["role"] == "parent"
    assert body["email"] == "sara@example.com"
    assert "password" not in body
    assert "password_hash" not in body

    async with session_factory() as session:
        user = await session.scalar(select(User))
    assert user is not None
    assert user.email == "sara@example.com"
    assert user.password_hash != "Parent1404"


async def test_duplicate_email_is_case_insensitive(client: AsyncClient) -> None:
    first = await client.post("/api/v1/auth/register", json=_payload())
    assert first.status_code == 201

    second = await client.post("/api/v1/auth/register", json=_payload(email="SARA@Example.com"))

    assert second.status_code == 409
    assert second.headers["content-type"].startswith("application/problem+json")
    assert second.json()["code"] == "email_already_registered"


async def test_weak_password_is_rejected_with_field_error(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json=_payload(password="abcdefgh", password_confirm="abcdefgh"),
    )

    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "validation_error"
    fields = {error["field"] for error in body["errors"]}
    assert "password" in fields


async def test_password_mismatch_is_field_error(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json=_payload(password_confirm="Different1404"),
    )

    assert response.status_code == 422
    fields = {error["field"] for error in response.json()["errors"]}
    assert "password_confirm" in fields


async def test_teacher_without_invite_is_forbidden(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/register", json=_payload(role="teacher"))

    assert response.status_code == 403
    assert response.json()["code"] == "invitation_required"


async def test_teacher_with_wrong_invite_is_forbidden(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register", json=_payload(role="teacher", invite_code="WRONG")
    )

    assert response.status_code == 403
    assert response.json()["code"] == "invitation_required"


async def test_teacher_with_invite_is_created_and_audited(
    client: AsyncClient, session_factory: async_sessionmaker[AsyncSession]
) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json=_payload(email="teacher@example.com", role="teacher", invite_code="TEST-INVITE-1404"),
    )

    assert response.status_code == 201, response.text
    assert response.json()["role"] == "teacher"

    async with session_factory() as session:
        audit = await session.scalar(
            select(AuditLog).where(AuditLog.action == "teacher.registered")
        )
    assert audit is not None
    assert audit.target_type == "user"
