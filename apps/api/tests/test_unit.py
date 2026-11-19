"""Unit tests for security primitives, validation and academic time."""

from __future__ import annotations

from datetime import UTC, date, datetime

import pytest
from pydantic import ValidationError

from app.core.security import (
    hash_password,
    invite_code_matches,
    new_refresh_token,
    verify_password,
)
from app.core.time import end_of_local_day, week_bounds
from app.schemas.auth import RegisterRequest


def test_password_hash_round_trip() -> None:
    hashed = hash_password("Parent1404")

    assert hashed != "Parent1404"
    assert verify_password("Parent1404", hashed) is True
    assert verify_password("Wrong1404", hashed) is False


def test_refresh_tokens_are_unique_and_hashed() -> None:
    first_raw, first_hash = new_refresh_token()
    second_raw, second_hash = new_refresh_token()

    assert first_raw != second_raw
    assert first_hash != second_hash
    assert len(first_hash) == 64
    assert first_raw not in first_hash


def test_teacher_invite_code_is_compared_exactly() -> None:
    assert invite_code_matches("TEST-INVITE-1404") is True
    assert invite_code_matches("test-invite-1404") is False
    assert invite_code_matches("") is False
    assert invite_code_matches(None) is False


def test_week_runs_saturday_to_friday() -> None:
    start, end = week_bounds(date(2026, 11, 19))  # Thursday

    assert start == date(2026, 11, 14)  # Saturday
    assert end == date(2026, 11, 20)  # Friday


def test_end_of_local_day_is_utc() -> None:
    moment = end_of_local_day(date(2026, 11, 19))

    # Tehran is UTC+03:30, so 23:59:59.999999 local is 20:29:59.999999Z.
    assert moment == datetime(2026, 11, 19, 20, 29, 59, 999999, tzinfo=UTC)


def test_password_policy_rejects_password_without_digits() -> None:
    with pytest.raises(ValidationError):
        RegisterRequest(
            full_name="سارا محمدی",
            email="sara@example.com",
            password="onlyletters",
            password_confirm="onlyletters",
            role="parent",
            accepted_terms=True,
        )


def test_terms_must_be_accepted() -> None:
    with pytest.raises(ValidationError):
        RegisterRequest(
            full_name="سارا محمدی",
            email="sara@example.com",
            password="Parent1404",
            password_confirm="Parent1404",
            role="parent",
            accepted_terms=False,
        )
