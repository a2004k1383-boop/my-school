"""Liveness and readiness endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session

router = APIRouter(tags=["system"])

VERSION = "0.1.0"


@router.get("/health", summary="Service health")
async def health(session: AsyncSession = Depends(get_session)) -> JSONResponse:
    try:
        await session.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001 - health must never raise
        return JSONResponse(
            status_code=503, content={"status": "degraded", "version": VERSION, "db": "error"}
        )
    return JSONResponse(status_code=200, content={"status": "ok", "version": VERSION, "db": "ok"})
