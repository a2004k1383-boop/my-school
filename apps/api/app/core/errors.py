"""RFC 7807 problem+json error handling with stable error codes."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

PROBLEM_MEDIA_TYPE = "application/problem+json"


class AppError(Exception):
    """Domain/application error that maps to a problem+json response."""

    def __init__(
        self,
        code: str,
        status_code: int,
        title: str,
        detail: str,
        errors: list[dict[str, str]] | None = None,
    ) -> None:
        super().__init__(detail)
        self.code = code
        self.status_code = status_code
        self.title = title
        self.detail = detail
        self.errors = errors or []


def problem_payload(
    code: str,
    title: str,
    status_code: int,
    detail: str,
    errors: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "type": f"https://myschool.local/errors/{code.replace('_', '-')}",
        "title": title,
        "status": status_code,
        "code": code,
        "detail": detail,
    }
    if errors:
        payload["errors"] = errors
    return payload


def error_response(
    code: str,
    title: str,
    status_code: int,
    detail: str,
    errors: list[dict[str, str]] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=problem_payload(code, title, status_code, detail, errors),
        media_type=PROBLEM_MEDIA_TYPE,
    )


def _field_errors(exc: RequestValidationError) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    for item in exc.errors():
        location = [str(part) for part in item.get("loc", []) if part != "body"]
        errors.append({"field": ".".join(location) or "body", "message": str(item.get("msg", ""))})
    return errors


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return error_response(exc.code, exc.title, exc.status_code, exc.detail, exc.errors)

    @app.exception_handler(RequestValidationError)
    async def _validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        return error_response(
            "validation_error",
            "Validation error",
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Some fields are invalid.",
            _field_errors(exc),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        details = {401: "Unauthorized", 403: "Forbidden", 404: "Not found"}
        code = {401: "unauthorized", 403: "forbidden", 404: "not_found"}.get(
            exc.status_code, "http_error"
        )
        return error_response(
            code,
            details.get(exc.status_code, "Request failed"),
            exc.status_code,
            str(exc.detail),
        )
