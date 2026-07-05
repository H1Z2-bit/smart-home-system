from fastapi import APIRouter, Depends, Query

from app.core.access import require_device_access, require_home_access
from app.core.deps import get_current_user
from app.core.permissions import Permission
from app.core.security import TokenPayload
from app.repositories.factory import (
    get_device_event_repository,
    get_device_repository,
    get_operation_log_repository,
    get_room_repository,
)
from app.schemas.device import DeviceControl, DeviceCreate, DeviceCreateCompat, DeviceUpdate
from app.services.device_service import DeviceService
from app.services.operation_log_service import OperationLogService
from app.utils.response import success_response

router = APIRouter(tags=["设备管理"])


def get_device_service() -> DeviceService:
    return DeviceService(
        get_device_repository(),
        get_room_repository(),
        get_device_event_repository(),
        OperationLogService(get_operation_log_repository()),
    )


@router.post("/homes/{home_id}/devices", summary="添加设备")
def create_device(home_id: int, payload: DeviceCreate, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_home_access(home_id, current_user, Permission.DEVICE_MANAGE)
    device = get_device_service().create_device(home_id, payload.model_dump(), current_user.user_id)
    return success_response(device)


@router.get("/homes/{home_id}/devices", summary="查询家庭空间下的设备列表")
def list_devices(
    home_id: int,
    room_id: int | None = Query(default=None, gt=0),
    current_user: TokenPayload = Depends(get_current_user),
) -> dict:
    require_home_access(home_id, current_user, Permission.HOME_VIEW)
    devices = get_device_service().list_devices(home_id, room_id)
    return success_response(devices)


@router.get("/devices/{device_id}", summary="查询设备详情")
def get_device(device_id: int, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_device_access(device_id, current_user, Permission.HOME_VIEW)
    device = get_device_service().get_device(device_id)
    return success_response(device)


@router.post("/devices/{device_id}/control", summary="控制设备")
def control_device(device_id: int, payload: DeviceControl, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_device_access(device_id, current_user, Permission.DEVICE_CONTROL)
    device = get_device_service().control_device(device_id, payload.model_dump(), current_user.user_id)
    return success_response(device)


@router.put("/devices/{device_id}", summary="修改设备")
def update_device(device_id: int, payload: DeviceUpdate, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_device_access(device_id, current_user, Permission.DEVICE_MANAGE)
    device = get_device_service().update_device(
        device_id,
        payload.model_dump(exclude_unset=True),
        current_user.user_id,
    )
    return success_response(device)


@router.delete("/devices/{device_id}", summary="删除设备")
def delete_device(device_id: int, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_device_access(device_id, current_user, Permission.DEVICE_MANAGE)
    result = get_device_service().delete_device(device_id, current_user.user_id)
    return success_response(result, "删除设备成功")


@router.get("/devices", summary="兼容旧接口：查询设备列表")
def list_devices_compat(
    home_id: int = Query(..., gt=0, description="家庭空间编号"),
    room_id: int | None = Query(default=None, gt=0, description="房间编号"),
    current_user: TokenPayload = Depends(get_current_user),
) -> dict:
    require_home_access(home_id, current_user, Permission.HOME_VIEW)
    devices = get_device_service().list_devices(home_id, room_id)
    return success_response(devices)


@router.post("/devices", summary="兼容旧接口：添加设备")
def create_device_compat(payload: DeviceCreateCompat, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    data = payload.model_dump()
    home_id = data.pop("home_id")
    require_home_access(home_id, current_user, Permission.DEVICE_MANAGE)
    device = get_device_service().create_device(home_id, data, current_user.user_id)
    return success_response(device)
