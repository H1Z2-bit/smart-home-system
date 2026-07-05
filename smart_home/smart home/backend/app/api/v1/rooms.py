from fastapi import APIRouter, Depends, Query

from app.core.access import require_home_access, require_room_access
from app.core.deps import get_current_user
from app.core.permissions import Permission
from app.core.security import TokenPayload
from app.repositories.factory import (
    get_device_repository,
    get_operation_log_repository,
    get_room_repository,
)
from app.schemas.room import RoomCreate, RoomCreateCompat, RoomUpdate
from app.services.operation_log_service import OperationLogService
from app.services.room_service import RoomService
from app.utils.response import success_response

router = APIRouter(tags=["房间管理"])


def get_room_service() -> RoomService:
    return RoomService(
        get_room_repository(),
        get_device_repository(),
        OperationLogService(get_operation_log_repository()),
    )


@router.post("/homes/{home_id}/rooms", summary="新增房间")
def create_room(home_id: int, payload: RoomCreate, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_home_access(home_id, current_user, Permission.HOME_MANAGE)
    room = get_room_service().create_room(home_id, payload.model_dump(), current_user.user_id)
    return success_response(room)


@router.get("/homes/{home_id}/rooms", summary="查询家庭空间下的房间列表")
def list_rooms(home_id: int, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_home_access(home_id, current_user, Permission.HOME_VIEW)
    rooms = get_room_service().list_rooms(home_id)
    return success_response(rooms)


@router.put("/rooms/{room_id}", summary="修改房间")
def update_room(room_id: int, payload: RoomUpdate, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_room_access(room_id, current_user, Permission.HOME_MANAGE)
    room = get_room_service().update_room(room_id, payload.model_dump(), current_user.user_id)
    return success_response(room)


@router.delete("/rooms/{room_id}", summary="删除房间")
def delete_room(room_id: int, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_room_access(room_id, current_user, Permission.HOME_MANAGE)
    result = get_room_service().delete_room(room_id, current_user.user_id)
    return success_response(result, "删除房间成功")


@router.get("/rooms", summary="兼容旧接口：查询房间列表")
def list_rooms_compat(
    home_id: int = Query(..., gt=0, description="家庭空间编号"),
    current_user: TokenPayload = Depends(get_current_user),
) -> dict:
    require_home_access(home_id, current_user, Permission.HOME_VIEW)
    rooms = get_room_service().list_rooms(home_id)
    return success_response(rooms)


@router.post("/rooms", summary="兼容旧接口：新增房间")
def create_room_compat(payload: RoomCreateCompat, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    data = payload.model_dump()
    home_id = data.pop("home_id")
    require_home_access(home_id, current_user, Permission.HOME_MANAGE)
    room = get_room_service().create_room(home_id, data, current_user.user_id)
    return success_response(room)
