"""Application factory and middleware wiring."""

from __future__ import annotations

import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.responses import Response

from app.api.v1.router import api_router
from app.core.config import ensure_sqlite_directory, get_settings
from app.core.errors import error_response, register_exception_handlers
from app.core.rate_limit import limiter

VERSION = "0.1.0"


def create_app() -> FastAPI:
    settings = get_settings()
    settings.validate_for_startup()
    ensure_sqlite_directory(settings.database_url)

    app = FastAPI(
        title=settings.app_name,
        version=VERSION,
        description="«مدرسه من» — school communication platform API",
    )
    app.state.limiter = limiter

    async def _rate_limit_handler(_: Request, __: Exception) -> Response:
        response = error_response(
            "rate_limited",
            "Too many requests",
            429,
            "تلاش‌های زیاد؛ چند دقیقه بعد دوباره امتحان کنید.",
        )
        response.headers["Retry-After"] = "60"
        return response

    app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)
    register_exception_handlers(app)

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )
    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
