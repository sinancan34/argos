"""Tests for the app-wide exception handlers in app/main.py.

Every handler is an async callable registered on the FastAPI app, so the unit
tests drive them directly with ``asyncio.run`` (the project pins no async test
plugin). The integration tests then prove the same envelopes come back over
HTTP through `client_no_raise`.
"""

import asyncio
import json
import logging

import pytest
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from limits import parse
from slowapi.errors import RateLimitExceeded
from slowapi.wrappers import Limit

from app.exceptions import AppException, ErrorDetail
from app.main import (
    _HTTP_STATUS_CODES,
    app_exception_handler,
    generic_exception_handler,
    http_exception_handler,
    rate_limit_handler,
    validation_exception_handler,
)
from tests.conftest import make_request


def _run(coro) -> JSONResponse:
    """Execute a handler coroutine and return its JSONResponse."""
    return asyncio.run(coro)


def _body(response: JSONResponse) -> dict:
    """Decode a JSONResponse body into a dict."""
    return json.loads(response.body)


def _rate_limit_exc(limit: str = "60/minute") -> RateLimitExceeded:
    """Build a real RateLimitExceeded for the configured limit string."""
    wrapped = Limit(
        parse(limit),
        lambda: "test-key",
        None,
        False,
        None,
        None,
        None,
        1,
        False,
    )
    return RateLimitExceeded(wrapped)


@pytest.mark.unit
class TestRateLimitHandler:
    def test_returns_429_envelope(self) -> None:
        # Arrange
        exc = _rate_limit_exc()

        # Act
        response = _run(rate_limit_handler(make_request(), exc))

        # Assert
        assert response.status_code == 429
        error = _body(response)["error"]
        assert error["code"] == "RATE_LIMIT_EXCEEDED"
        assert "60 per 1 minute" in error["message"]
        assert error["details"] == []

    def test_defaults_retry_after_to_60(self) -> None:
        # Arrange — slowapi's exception carries no retry_after attribute
        exc = _rate_limit_exc()

        # Act
        response = _run(rate_limit_handler(make_request(), exc))

        # Assert
        assert response.headers["Retry-After"] == "60"

    def test_uses_retry_after_when_present(self) -> None:
        # Arrange
        exc = _rate_limit_exc()
        exc.retry_after = 5

        # Act
        response = _run(rate_limit_handler(make_request(), exc))

        # Assert
        assert response.headers["Retry-After"] == "5"

    @pytest.mark.parametrize(
        "limit", ["1/second", "10/minute", "1000/hour", "5/day"]
    )
    def test_message_reports_the_breached_limit(self, limit: str) -> None:
        # Arrange
        exc = _rate_limit_exc(limit)

        # Act
        response = _run(rate_limit_handler(make_request(), exc))

        # Assert
        assert str(exc.detail) in _body(response)["error"]["message"]


@pytest.mark.unit
class TestAppExceptionHandler:
    def test_maps_status_code_and_message(self) -> None:
        # Arrange
        exc = AppException(status_code=404, code="NOT_FOUND", message="Device not found")

        # Act
        response = _run(app_exception_handler(make_request(), exc))

        # Assert
        assert response.status_code == 404
        assert _body(response)["error"] == {
            "code": "NOT_FOUND",
            "message": "Device not found",
            "details": [],
        }

    def test_serialises_details(self) -> None:
        # Arrange
        exc = AppException(
            status_code=422,
            code="VALIDATION_ERROR",
            message="Device not found",
            details=[
                ErrorDetail(
                    loc=["body", "device_id"],
                    message="Device not found",
                    type="value_error",
                )
            ],
        )

        # Act
        response = _run(app_exception_handler(make_request(), exc))

        # Assert
        details = _body(response)["error"]["details"]
        assert details == [
            {
                "loc": ["body", "device_id"],
                "message": "Device not found",
                "type": "value_error",
            }
        ]

    @pytest.mark.parametrize("status_code", [400, 404, 409, 422, 500, 418])
    def test_passes_through_any_status_code(self, status_code: int) -> None:
        # Arrange
        exc = AppException(status_code=status_code, code="X", message="m")

        # Act
        response = _run(app_exception_handler(make_request(), exc))

        # Assert
        assert response.status_code == status_code


@pytest.mark.unit
class TestValidationExceptionHandler:
    def test_maps_pydantic_errors_to_details(self) -> None:
        # Arrange
        exc = RequestValidationError(
            [
                {
                    "loc": ("body", "name"),
                    "msg": "Field required",
                    "type": "missing",
                },
                {
                    "loc": ("body", "steps", 0, "command"),
                    "msg": "Unknown command",
                    "type": "value_error",
                },
            ]
        )

        # Act
        response = _run(validation_exception_handler(make_request(), exc))

        # Assert
        assert response.status_code == 422
        error = _body(response)["error"]
        assert error["code"] == "VALIDATION_ERROR"
        assert error["message"] == "Request validation failed"
        assert error["details"][0]["loc"] == ["body", "name"]
        assert error["details"][1]["loc"] == ["body", "steps", "0", "command"]

    def test_empty_error_list_yields_empty_details(self) -> None:
        # Arrange
        exc = RequestValidationError([])

        # Act
        response = _run(validation_exception_handler(make_request(), exc))

        # Assert
        assert _body(response)["error"]["details"] == []

    def test_missing_keys_fall_back_to_empty_values(self) -> None:
        # Arrange — a malformed error dict must not crash the handler
        exc = RequestValidationError([{}])

        # Act
        response = _run(validation_exception_handler(make_request(), exc))

        # Assert
        assert _body(response)["error"]["details"] == [
            {"loc": [], "message": "", "type": ""}
        ]


@pytest.mark.unit
class TestHttpExceptionHandler:
    @pytest.mark.parametrize(
        ("status_code", "expected_code"), sorted(_HTTP_STATUS_CODES.items())
    )
    def test_known_status_codes_map_to_names(
        self, status_code: int, expected_code: str
    ) -> None:
        # Arrange
        exc = HTTPException(status_code=status_code, detail="boom")

        # Act
        response = _run(http_exception_handler(make_request(), exc))

        # Assert
        assert response.status_code == status_code
        assert _body(response)["error"]["code"] == expected_code

    @pytest.mark.parametrize("status_code", [418, 451, 503])
    def test_unmapped_status_codes_fall_back_to_the_number(
        self, status_code: int
    ) -> None:
        # Arrange
        exc = HTTPException(status_code=status_code, detail="teapot")

        # Act
        response = _run(http_exception_handler(make_request(), exc))

        # Assert
        assert _body(response)["error"]["code"] == str(status_code)

    def test_non_string_detail_is_stringified(self) -> None:
        # Arrange
        exc = HTTPException(status_code=400, detail={"field": "name"})

        # Act
        response = _run(http_exception_handler(make_request(), exc))

        # Assert
        assert _body(response)["error"]["message"] == "{'field': 'name'}"


@pytest.mark.unit
class TestGenericExceptionHandler:
    def test_returns_opaque_500_envelope(self) -> None:
        # Arrange
        exc = RuntimeError("connection string postgres://user:hunter2@db")

        # Act
        response = _run(generic_exception_handler(make_request(), exc))

        # Assert
        assert response.status_code == 500
        assert _body(response)["error"] == {
            "code": "INTERNAL_ERROR",
            "message": "Internal server error",
            "details": [],
        }

    def test_does_not_leak_exception_text(self) -> None:
        # Arrange
        exc = RuntimeError("hunter2")

        # Act
        response = _run(generic_exception_handler(make_request(), exc))

        # Assert
        assert b"hunter2" not in response.body

    def test_logs_the_exception(self, caplog) -> None:
        # Arrange
        exc = ValueError("kaboom")

        # Act
        with caplog.at_level(logging.ERROR, logger="app.main"):
            _run(generic_exception_handler(make_request(), exc))

        # Assert
        assert "kaboom" in caplog.text

    @pytest.mark.parametrize(
        "exc",
        [
            ValueError("bad value"),
            KeyError("missing"),
            ZeroDivisionError("division by zero"),
            OverflowError("Python int too large to convert to SQLite INTEGER"),
        ],
    )
    def test_handles_any_exception_type(self, exc: Exception) -> None:
        # Act
        response = _run(generic_exception_handler(make_request(), exc))

        # Assert
        assert response.status_code == 500


@pytest.mark.integration
class TestHandlersOverHttp:
    def test_unhandled_dependency_error_returns_500_envelope(
        self, client_no_raise
    ) -> None:
        # Arrange
        from app.database import get_db
        from app.main import app

        def _boom():
            raise RuntimeError("secret connection details")
            yield  # pragma: no cover - generator marker

        app.dependency_overrides[get_db] = _boom

        # Act
        response = client_no_raise.get("/api/v1/devices")

        # Assert
        assert response.status_code == 500
        assert response.json()["error"]["code"] == "INTERNAL_ERROR"
        assert "secret" not in response.text

    @pytest.mark.parametrize(
        ("method", "path"),
        [
            ("PUT", "/api/v1/devices"),
            ("PUT", "/api/v1/scenarios"),
            ("GET", "/api/v1/does-not-exist"),
            ("GET", "/nope"),
        ],
    )
    def test_routing_errors_escape_the_error_envelope(
        self, client, method: str, path: str
    ) -> None:
        # Act
        response = client.request(method, path)

        # KNOWN DEFECT: the custom handler is registered against FastAPI's
        # HTTPException subclass, but the routing layer raises Starlette's base
        # class, which still resolves to FastAPI's default handler. So 404/405
        # return {"detail": ...} while every endpoint-raised error returns
        # {"error": {...}} — clients parsing error.code break on these.
        assert response.status_code in (404, 405)
        assert "error" not in response.json()
        assert "detail" in response.json()

    def test_endpoint_raised_errors_do_use_the_envelope(self, client) -> None:
        # Act — routers raise AppException, which has its own handler
        response = client.get("/api/v1/devices/ghost")

        # Assert
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "NOT_FOUND"

    def test_validation_error_envelope_shape(self, client) -> None:
        # Act
        response = client.post("/api/v1/devices", json={})

        # Assert
        assert response.status_code == 422
        error = response.json()["error"]
        assert error["code"] == "VALIDATION_ERROR"
        assert error["details"][0]["loc"] == ["body", "name"]
        assert error["details"][0]["type"] == "missing"

    def test_rate_limiting_is_registered_but_never_enforced(self, client) -> None:
        # Arrange — the configured budget, parsed from settings
        from app.config import settings
        from app.main import limiter

        budget = int(settings.rate_limit.split("/")[0])

        # Act — deliberately exceed the budget from one client address
        statuses = {client.get("/health").status_code for _ in range(budget + 15)}

        # KNOWN DEFECT: `app.state.limiter` and the 429 handler are wired up,
        # but `SlowAPIMiddleware` is never added and no route carries
        # `@limiter.limit`, so `default_limits` never runs. Every router
        # documents a 429 response that cannot currently be produced.
        assert statuses == {200}
        assert limiter._default_limits, "a default limit is configured"

    def test_cors_headers_are_applied(self, client) -> None:
        # Act
        response = client.get(
            "/api/v1/devices", headers={"Origin": "http://localhost:3000"}
        )

        # Assert
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
