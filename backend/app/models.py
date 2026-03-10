import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uuid() -> str:
    return str(uuid.uuid4())


class Scenario(Base):
    __tablename__ = "scenarios"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    url: Mapped[str] = mapped_column(String, nullable=False)
    timeout: Mapped[int] = mapped_column(Integer, nullable=False, default=5000)
    validation_timeout: Mapped[int] = mapped_column(Integer, nullable=False, default=10000)
    steps: Mapped[list] = mapped_column(JSON, nullable=False)
    validations: Mapped[list] = mapped_column(JSON, nullable=False)
    created_at: Mapped[str] = mapped_column(String, nullable=False, default=_utcnow_iso)
    updated_at: Mapped[str] = mapped_column(String, nullable=False, default=_utcnow_iso, onupdate=_utcnow_iso)

    runs: Mapped[list["TestRun"]] = relationship(back_populates="scenario")


class TestRun(Base):
    __tablename__ = "test_runs"
    __table_args__ = (
        Index("ix_test_runs_scenario_id", "scenario_id"),
        Index("ix_test_runs_started_at", "started_at"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    scenario_id: Mapped[str] = mapped_column(String, ForeignKey("scenarios.id"), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    error_type: Mapped[str | None] = mapped_column(String, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)
    started_at: Mapped[str] = mapped_column(String, nullable=False, default=_utcnow_iso)
    finished_at: Mapped[str | None] = mapped_column(String, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    scenario: Mapped["Scenario"] = relationship(back_populates="runs")
    results: Mapped[list["TestRunResult"]] = relationship(back_populates="run")


class TestRunResult(Base):
    __tablename__ = "test_run_results"
    __table_args__ = (
        Index("ix_test_run_results_run_id", "run_id"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    run_id: Mapped[str] = mapped_column(String, ForeignKey("test_runs.id"), nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    ref_id: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    error_type: Mapped[str | None] = mapped_column(String, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)
    actual_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    screenshot_path: Mapped[str | None] = mapped_column(String, nullable=True)
    executed_at: Mapped[str] = mapped_column(String, nullable=False, default=_utcnow_iso)

    run: Mapped["TestRun"] = relationship(back_populates="results")
