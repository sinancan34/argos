import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, CheckConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uuid() -> str:
    return str(uuid.uuid4())


class Scenario(Base):
    __tablename__ = "scenarios"
    __table_args__ = (
        CheckConstraint("status IN (0, 1)", name="ck_scenario_status"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    step_timeout: Mapped[int] = mapped_column(Integer, nullable=False, default=5000)
    validation_timeout: Mapped[int] = mapped_column(Integer, nullable=False, default=10000)
    steps: Mapped[list] = mapped_column(JSON, nullable=False)
    validations: Mapped[list] = mapped_column(JSON, nullable=False)
    created_at: Mapped[str] = mapped_column(String, nullable=False, default=_utcnow_iso)
    updated_at: Mapped[str] = mapped_column(String, nullable=False, default=_utcnow_iso, onupdate=_utcnow_iso)
