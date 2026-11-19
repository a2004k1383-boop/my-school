"""Async engine and request-scoped session dependency."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import ensure_sqlite_directory, get_settings

_settings = get_settings()
ensure_sqlite_directory(_settings.database_url)

engine = create_async_engine(_settings.database_url, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield a session per request and always close it."""
    async with SessionLocal() as session:
        yield session
