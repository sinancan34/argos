import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Scenario
from app.schemas import (
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


@router.post("", status_code=201, response_model=SingleScenarioEnvelope)
def create_scenario(payload: ScenarioCreate, db: Session = Depends(get_db)):
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
    return SingleScenarioEnvelope(data=ScenarioResponse.model_validate(scenario))


@router.get("/{scenario_id}", response_model=SingleScenarioEnvelope)
def get_scenario(scenario_id: str, db: Session = Depends(get_db)):
    scenario = db.get(Scenario, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return SingleScenarioEnvelope(data=ScenarioResponse.model_validate(scenario))


@router.patch("/{scenario_id}", response_model=SingleScenarioEnvelope)
def update_scenario(
    scenario_id: str, payload: ScenarioUpdate, db: Session = Depends(get_db)
):
    scenario = db.get(Scenario, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "steps" and value is not None:
            value = [s.model_dump() if hasattr(s, "model_dump") else s for s in value]
        if key == "validations" and value is not None:
            value = [v.model_dump() if hasattr(v, "model_dump") else v for v in value]
        setattr(scenario, key, value)

    db.commit()
    db.refresh(scenario)
    return SingleScenarioEnvelope(data=ScenarioResponse.model_validate(scenario))


@router.delete("/{scenario_id}", status_code=204)
def delete_scenario(scenario_id: str, db: Session = Depends(get_db)):
    scenario = db.get(Scenario, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    db.delete(scenario)
    db.commit()


@router.get("", response_model=ScenarioListEnvelope)
def list_scenarios(
    name: str | None = None,
    status: int | None = None,
    sort_by: SortBy = SortBy.created_at,
    sort_order: SortOrder = SortOrder.desc,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Scenario)

    if name:
        query = query.filter(Scenario.name.ilike(f"%{name}%"))

    if status is not None:
        query = query.filter(Scenario.status == status)

    total_count = query.count()

    sort_column = getattr(Scenario, sort_by.value)
    if sort_order == SortOrder.desc:
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()

    query = query.order_by(sort_column)

    offset = (page - 1) * size
    scenarios = query.offset(offset).limit(size).all()

    total_pages = math.ceil(total_count / size) if total_count > 0 else 0

    return ScenarioListEnvelope(
        data=[ScenarioResponse.model_validate(s) for s in scenarios],
        meta=PaginationMeta(
            page=page,
            size=size,
            total_count=total_count,
            total_pages=total_pages,
        ),
    )
