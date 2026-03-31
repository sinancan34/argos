from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import ErrorBody, ErrorEnvelope

router = APIRouter(tags=["health"])


class HealthData(BaseModel):
    status: str
    database: str


class HealthEnvelope(BaseModel):
    data: HealthData


@router.get(
    "/health",
    response_model=HealthEnvelope,
    summary="Health check",
    description="Check API and database health.",
    responses={503: {"model": ErrorEnvelope}},
)
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return HealthEnvelope(
            data=HealthData(status="healthy", database="connected")
        )
    except Exception:
        envelope = ErrorEnvelope(
            error=ErrorBody(
                code="SERVICE_UNAVAILABLE",
                message="Database connection failed",
            )
        )
        return JSONResponse(
            status_code=503,
            content=envelope.model_dump(),
        )
