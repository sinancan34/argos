import logging

from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings
from app.exceptions import AppException, ErrorBody, ErrorDetail, ErrorEnvelope
from app.routers.devices import router as devices_router
from app.routers.health import router as health_router
from app.routers.scenarios import router as scenarios_router

logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.rate_limit],
    headers_enabled=True,
)

app = FastAPI(title="Argos", description="Pixel Code Audit Tool", version="1.0.0")
app.state.limiter = limiter

# CORS — parse comma-separated origins from config
_origins = [
    o.strip() for o in settings.cors_allowed_origins.split(",") if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Exception handlers ---


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(
    _request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    envelope = ErrorEnvelope(
        error=ErrorBody(
            code="RATE_LIMIT_EXCEEDED",
            message=f"Rate limit exceeded: {exc.detail}",
        )
    )
    return JSONResponse(
        status_code=429,
        content=envelope.model_dump(),
        headers={"Retry-After": str(getattr(exc, "retry_after", 60))},
    )


@app.exception_handler(AppException)
async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
    envelope = ErrorEnvelope(
        error=ErrorBody(code=exc.code, message=exc.message, details=exc.details)
    )
    return JSONResponse(
        status_code=exc.status_code, content=envelope.model_dump()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    details = [
        ErrorDetail(
            loc=[str(p) for p in err.get("loc", [])],
            message=err.get("msg", ""),
            type=err.get("type", ""),
        )
        for err in exc.errors()
    ]
    envelope = ErrorEnvelope(
        error=ErrorBody(
            code="VALIDATION_ERROR",
            message="Request validation failed",
            details=details,
        )
    )
    return JSONResponse(status_code=422, content=envelope.model_dump())


_HTTP_STATUS_CODES: dict[int, str] = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    410: "GONE",
    422: "UNPROCESSABLE_ENTITY",
    500: "INTERNAL_ERROR",
}


@app.exception_handler(HTTPException)
async def http_exception_handler(
    _request: Request, exc: HTTPException
) -> JSONResponse:
    code = _HTTP_STATUS_CODES.get(exc.status_code, str(exc.status_code))
    envelope = ErrorEnvelope(
        error=ErrorBody(code=code, message=str(exc.detail))
    )
    return JSONResponse(
        status_code=exc.status_code, content=envelope.model_dump()
    )


@app.exception_handler(Exception)
async def generic_exception_handler(
    _request: Request, exc: Exception
) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    envelope = ErrorEnvelope(
        error=ErrorBody(code="INTERNAL_ERROR", message="Internal server error")
    )
    return JSONResponse(status_code=500, content=envelope.model_dump())


# Health check lives at root (outside version prefix)
app.include_router(health_router)

# All API routes under /api/v1
api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(devices_router)
api_v1.include_router(scenarios_router)
app.include_router(api_v1)
