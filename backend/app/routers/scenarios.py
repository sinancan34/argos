import math

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import AppException, ErrorEnvelope
from app.models import Scenario
from app.schemas import (
    DeleteData,
    DeleteScenarioEnvelope,
    PaginationLinks,
    PaginationMeta,
    ScenarioCreate,
    ScenarioListEnvelope,
    ScenarioResponse,
    ScenarioStatus,
    ScenarioUpdate,
    SingleScenarioEnvelope,
    SortBy,
    SortOrder,
)

router = APIRouter(prefix="/scenarios", tags=["scenarios"])

_LIKE_ESCAPE_CHAR = "\\"


def _escape_like(value: str) -> str:
    """Escape SQL LIKE wildcard characters so they are matched literally."""
    return (
        value.replace(_LIKE_ESCAPE_CHAR, _LIKE_ESCAPE_CHAR * 2)
        .replace("%", f"{_LIKE_ESCAPE_CHAR}%")
        .replace("_", f"{_LIKE_ESCAPE_CHAR}_")
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
    scenario = Scenario(
        name=payload.name,
        description=payload.description,
        status=payload.status,
        step_timeout=payload.step_timeout,
        validation_timeout=payload.validation_timeout,
        steps=[s.model_dump() for s in payload.steps],
        validations=[v.model_dump() for v in payload.validations],
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


def _build_pagination_links(
    request: Request, page: int, size: int, total_pages: int
) -> PaginationLinks:
    """Build self/first/last/next/prev links preserving current query params."""
    base = str(request.url).split("?")[0]
    # Preserve non-pagination query params
    extra = {
        k: v
        for k, v in request.query_params.items()
        if k not in ("page", "size")
    }

    def _url(p: int) -> str:
        params = {**extra, "page": str(p), "size": str(size)}
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{base}?{qs}"

    last_page = max(total_pages, 1)
    return PaginationLinks(
        self=_url(page),
        first=_url(1),
        last=_url(last_page),
        next=_url(page + 1) if page < last_page else None,
        prev=_url(page - 1) if page > 1 else None,
    )


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
    status: ScenarioStatus | None = None,
    sort_by: SortBy = SortBy.created_at,
    sort_order: SortOrder = SortOrder.desc,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    stmt = select(Scenario)

    if name:
        escaped = _escape_like(name)
        stmt = stmt.where(
            Scenario.name.ilike(f"%{escaped}%", escape=_LIKE_ESCAPE_CHAR)
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
        links=_build_pagination_links(request, page, size, total_pages),
    )
