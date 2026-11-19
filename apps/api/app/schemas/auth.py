"""Request/response schemas for the identity module."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user import Role

PASSWORD_MIN = 8
PASSWORD_MAX = 128


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(min_length=PASSWORD_MIN, max_length=PASSWORD_MAX)
    password_confirm: str = Field(min_length=PASSWORD_MIN, max_length=PASSWORD_MAX)
    role: Role
    invite_code: str | None = Field(default=None, max_length=128)
    accepted_terms: bool

    @field_validator("full_name")
    @classmethod
    def _clean_full_name(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if len(cleaned) < 3:
            raise ValueError("Name must be at least 3 characters")
        if any(ord(char) < 32 for char in cleaned):
            raise ValueError("Name contains invalid characters")
        return cleaned

    @field_validator("password")
    @classmethod
    def _password_strength(cls, value: str) -> str:
        if not any(char.isalpha() for char in value):
            raise ValueError("Password must contain at least one letter")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit")
        return value

    @field_validator("password_confirm")
    @classmethod
    def _passwords_match(cls, value: str, info) -> str:
        if value != info.data.get("password"):
            raise ValueError("Passwords do not match")
        return value

    @field_validator("accepted_terms")
    @classmethod
    def _terms_accepted(cls, value: bool) -> bool:
        if not value:
            raise ValueError("Terms must be accepted")
        return value

    @field_validator("invite_code")
    @classmethod
    def _trim_invite_code(cls, value: str | None) -> str | None:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=PASSWORD_MAX)
    remember_me: bool = False


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    email: str
    role: Role
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserPublic


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
