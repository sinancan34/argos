import math

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import AppException, ErrorEnvelope
from app.models import Device, Scenario
from app.routers._common import LIKE_ESCAPE_CHAR, build_pagination_links, escape_like
from app.schemas import (
    DeleteData,
    DeleteDeviceEnvelope,
    DeviceCreate,
    DeviceListEnvelope,
    DeviceResponse,
    DeviceUpdate,
    PaginationMeta,
    SingleDeviceEnvelope,
    SortBy,
    SortOrder,
)

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post(
    "",
    status_code=201,
    response_model=SingleDeviceEnvelope,
    summary="Create device",
    description="Create a new device emulation profile.",
    responses={422: {"model": ErrorEnvelope}, 429: {"model": ErrorEnvelope}},
)
def create_device(
    payload: DeviceCreate, request: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    device = Device(
        name=payload.name,
        meta=payload.meta,
        status=payload.status,
    )
    db.add(device)
    db.commit()
    db.refresh(device)

    envelope = SingleDeviceEnvelope(data=DeviceResponse.model_validate(device))
    location = f"/api/v1/devices/{device.id}"
    return JSONResponse(
        status_code=201,
        content=envelope.model_dump(),
        headers={"Location": location},
    )


@router.get(
    "/{device_id}",
    response_model=SingleDeviceEnvelope,
    summary="Get device",
    description="Retrieve a single device by ID.",
    responses={404: {"model": ErrorEnvelope}, 429: {"model": ErrorEnvelope}},
)
def get_device(device_id: str, request: Request, db: Session = Depends(get_db)):
    device = db.get(Device, device_id)
    if not device:
        raise AppException(
            status_code=404, code="NOT_FOUND", message="Device not found"
        )
    return SingleDeviceEnvelope(data=DeviceResponse.model_validate(device))


@router.patch(
    "/{device_id}",
    response_model=SingleDeviceEnvelope,
    summary="Update device",
    description="Partially update a device. Only provided fields are changed.",
    responses={
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def update_device(
    device_id: str, payload: DeviceUpdate, request: Request, db: Session = Depends(get_db)
):
    device = db.get(Device, device_id)
    if not device:
        raise AppException(
            status_code=404, code="NOT_FOUND", message="Device not found"
        )

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(device, key, value)

    db.commit()
    db.refresh(device)
    return SingleDeviceEnvelope(data=DeviceResponse.model_validate(device))


@router.delete(
    "/{device_id}",
    response_model=DeleteDeviceEnvelope,
    summary="Delete device",
    description="Delete a device. Blocked (409) if any scenario references it.",
    responses={
        404: {"model": ErrorEnvelope},
        409: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def delete_device(device_id: str, request: Request, db: Session = Depends(get_db)):
    device = db.get(Device, device_id)
    if not device:
        raise AppException(
            status_code=404, code="NOT_FOUND", message="Device not found"
        )

    reference_count = db.execute(
        select(func.count())
        .select_from(Scenario)
        .where(Scenario.device_id == device_id)
    ).scalar_one()
    if reference_count > 0:
        raise AppException(
            status_code=409,
            code="CONFLICT",
            message="Device is in use by one or more scenarios",
        )

    db.delete(device)
    db.commit()
    return DeleteDeviceEnvelope(data=DeleteData(id=device_id))


@router.get(
    "",
    response_model=DeviceListEnvelope,
    summary="List devices",
    description="List devices with pagination, filtering, and sorting.",
    responses={422: {"model": ErrorEnvelope}, 429: {"model": ErrorEnvelope}},
)
def list_devices(
    request: Request,
    name: str | None = None,
    status: bool | None = None,
    sort_by: SortBy = SortBy.created_at,
    sort_order: SortOrder = SortOrder.desc,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    stmt = select(Device)

    if name:
        escaped = escape_like(name)
        stmt = stmt.where(
            Device.name.ilike(f"%{escaped}%", escape=LIKE_ESCAPE_CHAR)
        )

    if status is not None:
        stmt = stmt.where(Device.status == status)

    total_count = db.execute(
        select(func.count()).select_from(stmt.subquery())
    ).scalar_one()

    sort_column = getattr(Device, sort_by.value)
    if sort_order == SortOrder.desc:
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()

    stmt = stmt.order_by(sort_column)

    offset = (page - 1) * size
    devices = db.execute(stmt.offset(offset).limit(size)).scalars().all()

    total_pages = math.ceil(total_count / size) if total_count > 0 else 0

    return DeviceListEnvelope(
        data=[DeviceResponse.model_validate(d) for d in devices],
        meta=PaginationMeta(
            page=page,
            size=size,
            total_count=total_count,
            total_pages=total_pages,
        ),
        links=build_pagination_links(request, page, size, total_pages),
    )
