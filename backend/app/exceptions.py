from pydantic import BaseModel


class ErrorDetail(BaseModel):
    loc: list[str]
    message: str
    type: str


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] = []


class ErrorEnvelope(BaseModel):
    error: ErrorBody


class AppException(Exception):
    """Application-level exception that produces a consistent error envelope."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: list[ErrorDetail] | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or []
        super().__init__(message)
