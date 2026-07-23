import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uuid() -> str:
    return str(uuid.uuid4())


class Device(Base):
    """An emulation profile a scenario runs against (name + free-form meta)."""

    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String, nullable=False)
    meta: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[str] = mapped_column(String, nullable=False, default=_utcnow_iso)
    updated_at: Mapped[str] = mapped_column(String, nullable=False, default=_utcnow_iso, onupdate=_utcnow_iso)

    scenarios: Mapped[list["Scenario"]] = relationship(back_populates="device")


class Scenario(Base):
    __tablename__ = "scenarios"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    step_timeout: Mapped[int] = mapped_column(Integer, nullable=False, default=5000)
    validation_timeout: Mapped[int] = mapped_column(Integer, nullable=False, default=10000)
    steps: Mapped[list] = mapped_column(JSON, nullable=False)
    validations: Mapped[list] = mapped_column(JSON, nullable=False)
    device_id: Mapped[str] = mapped_column(
        String, ForeignKey("devices.id"), nullable=False
    )
    created_at: Mapped[str] = mapped_column(String, nullable=False, default=_utcnow_iso)
    updated_at: Mapped[str] = mapped_column(String, nullable=False, default=_utcnow_iso, onupdate=_utcnow_iso)

    device: Mapped["Device"] = relationship(back_populates="scenarios")
