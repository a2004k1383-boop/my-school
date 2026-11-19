"""Seed demo users for local development and the demo script."""

from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import Role, User

DEMO_PASSWORD = "Demo1234"

DEMO_USERS: list[tuple[str, str, Role]] = [
    ("parent@demo.example.com", "مریم احمدی", Role.parent),
    ("student@demo.example.com", "علی احمدی", Role.student),
    ("teacher@demo.example.com", "رضا کریمی", Role.teacher),
]


async def seed() -> None:
    settings = get_settings()
    if settings.is_production:
        raise SystemExit("Refusing to seed demo data in production")

    async with SessionLocal() as session:
        for email, full_name, role in DEMO_USERS:
            existing = await session.scalar(select(User).where(User.email == email))
            if existing is not None:
                continue
            session.add(
                User(
                    email=email,
                    full_name=full_name,
                    role=role,
                    password_hash=hash_password(DEMO_PASSWORD),
                )
            )
        await session.commit()

    print(f"Seeded {len(DEMO_USERS)} demo users (password: {DEMO_PASSWORD})")


if __name__ == "__main__":
    asyncio.run(seed())
