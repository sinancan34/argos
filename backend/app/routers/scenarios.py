import math

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import AppException, ErrorDetail, ErrorEnvelope
from app.models import Device, Scenario
from app.routers._common import LIKE_ESCAPE_CHAR, build_pagination_links, escape_like
from app.schemas import (
    DeleteData,
    DeleteScenarioEnvelope,
    PaginationMeta,
    ScenarioCreate,
    ScenarioListEnvelope,
    ScenarioResponse,
    ScenarioUpdate,
    SingleScenarioEnvelope,
    SortBy,
    SortOrder,
)

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


def _require_device(db: Session, device_id: str) -> None:
    """Ensure the referenced device exists (SQLite FK enforcement is off)."""
    if not db.get(Device, device_id):
        raise AppException(
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


@router.post(
    "",
    status_code=201,
    response_model=SingleScenarioEnvelope,
    summary="Create scenario",
    description="Create a new test scenario with steps and validations.",
    responses={422: {"model": ErrorEnvelope}, 429: {"model": ErrorEnvelope}},
)
def create_scenario(
    payload: ScenarioCreate, request: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    _require_device(db, payload.device_id)
    scenario = Scenario(
        name=payload.name,
        description=payload.description,
        status=payload.status,
        step_timeout=payload.step_timeout,
        validation_timeout=payload.validation_timeout,
        steps=[s.model_dump() for s in payload.steps],
        validations=[v.model_dump() for v in payload.validations],
        device_id=payload.device_id,
    )
    db.add(scenario)
    db.commit()
    db.refresh(scenario)

    envelope = SingleScenarioEnvelope(
        data=ScenarioResponse.model_validate(scenario)
    )
    location = f"/api/v1/scenarios/{scenario.id}"
    return JSONResponse(
        status_code=201,
        content=envelope.model_dump(),
        headers={"Location": location},
    )


@router.get(
    "/{scenario_id}",
    response_model=SingleScenarioEnvelope,
    summary="Get scenario",
    description="Retrieve a single scenario by ID.",
    responses={404: {"model": ErrorEnvelope}, 429: {"model": ErrorEnvelope}},
)
def get_scenario(scenario_id: str, request: Request, db: Session = Depends(get_db)):
    scenario = db.get(Scenario, scenario_id)
    if not scenario:
        raise AppException(
            status_code=404, code="NOT_FOUND", message="Scenario not found"
        )
    return SingleScenarioEnvelope(data=ScenarioResponse.model_validate(scenario))


@router.patch(
    "/{scenario_id}",
    response_model=SingleScenarioEnvelope,
    summary="Update scenario",
    description="Partially update a scenario. Only provided fields are changed.",
    responses={
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def update_scenario(
    scenario_id: str, payload: ScenarioUpdate, request: Request, db: Session = Depends(get_db)
):
    scenario = db.get(Scenario, scenario_id)
    if not scenario:
        raise AppException(
            status_code=404, code="NOT_FOUND", message="Scenario not found"
        )

    update_data = payload.model_dump(exclude_unset=True)
    if "device_id" in update_data and payload.device_id is not None:
        _require_device(db, payload.device_id)
    if "steps" in update_data and payload.steps is not None:
        update_data["steps"] = [s.model_dump() for s in payload.steps]
    if "validations" in update_data and payload.validations is not None:
        update_data["validations"] = [v.model_dump() for v in payload.validations]
    for key, value in update_data.items():
        setattr(scenario, key, value)

    db.commit()
    db.refresh(scenario)
    return SingleScenarioEnvelope(data=ScenarioResponse.model_validate(scenario))


@router.delete(
    "/{scenario_id}",
    response_model=DeleteScenarioEnvelope,
    summary="Delete scenario",
    description="Permanently delete a scenario.",
    responses={404: {"model": ErrorEnvelope}, 429: {"model": ErrorEnvelope}},
)
def delete_scenario(scenario_id: str, request: Request, db: Session = Depends(get_db)):
    scenario = db.get(Scenario, scenario_id)
    if not scenario:
        raise AppException(
            status_code=404, code="NOT_FOUND", message="Scenario not found"
        )
    db.delete(scenario)
    db.commit()
    return DeleteScenarioEnvelope(data=DeleteData(id=scenario_id))


@router.get(
    "",
    response_model=ScenarioListEnvelope,
    summary="List scenarios",
    description="List scenarios with pagination, filtering, and sorting.",
    responses={422: {"model": ErrorEnvelope}, 429: {"model": ErrorEnvelope}},
)
def list_scenarios(
    request: Request,
    name: str | None = None,
    status: bool | None = None,
    sort_by: SortBy = SortBy.created_at,
    sort_order: SortOrder = SortOrder.desc,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    stmt = select(Scenario)

    if name:
        escaped = escape_like(name)
        stmt = stmt.where(
            Scenario.name.ilike(f"%{escaped}%", escape=LIKE_ESCAPE_CHAR)
        )

    if status is not None:
        stmt = stmt.where(Scenario.status == status)

    total_count = db.execute(
        select(func.count()).select_from(stmt.subquery())
    ).scalar_one()

    sort_column = getattr(Scenario, sort_by.value)
    if sort_order == SortOrder.desc:
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()

    stmt = stmt.order_by(sort_column)

    offset = (page - 1) * size
    scenarios = db.execute(stmt.offset(offset).limit(size)).scalars().all()

    total_pages = math.ceil(total_count / size) if total_count > 0 else 0

    return ScenarioListEnvelope(
        data=[ScenarioResponse.model_validate(s) for s in scenarios],
        meta=PaginationMeta(
            page=page,
            size=size,
            total_count=total_count,
            total_pages=total_pages,
        ),
        links=build_pagination_links(request, page, size, total_pages),
    )
