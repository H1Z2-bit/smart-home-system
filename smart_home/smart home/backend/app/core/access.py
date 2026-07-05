from typing import Any

from app.core.permissions import Permission
from app.core.security import TokenPayload
from app.repositories.factory import (
    get_alarm_repository,
    get_device_repository,
    get_linkage_repository,
    get_room_repository,
    get_scene_repository,
    get_schedule_repository,
)
from app.services.permission_service import PermissionService
from app.utils.response import AppException


def require_home_access(home_id: int, current_user: TokenPayload, permission: Permission) -> None:
    PermissionService().require_home_permission(home_id, current_user.user_id, permission)


def require_room_access(room_id: int, current_user: TokenPayload, permission: Permission) -> dict[str, Any]:
    room = get_room_repository().get(room_id)
    if room is None:
        raise AppException(404, "房间不存在")
    require_home_access(room["home_id"], current_user, permission)
    return room


def require_device_access(device_id: int, current_user: TokenPayload, permission: Permission) -> dict[str, Any]:
    device = get_device_repository().get(device_id)
    if device is None:
        raise AppException(404, "设备不存在")
    require_home_access(device["home_id"], current_user, permission)
    return device


def require_scene_access(scene_id: int, current_user: TokenPayload, permission: Permission) -> dict[str, Any]:
    scene = get_scene_repository().get(scene_id)
    if scene is None:
        raise AppException(404, "情景模式不存在")
    require_home_access(scene["home_id"], current_user, permission)
    return scene


def require_schedule_access(task_id: int, current_user: TokenPayload, permission: Permission) -> dict[str, Any]:
    task = get_schedule_repository().get(task_id)
    if task is None:
        raise AppException(404, "定时任务不存在")
    require_home_access(task["home_id"], current_user, permission)
    return task


def require_linkage_access(rule_id: int, current_user: TokenPayload, permission: Permission) -> dict[str, Any]:
    rule = get_linkage_repository().get(rule_id)
    if rule is None:
        raise AppException(404, "联动规则不存在")
    require_home_access(rule["home_id"], current_user, permission)
    return rule


def require_alarm_access(alarm_id: int, current_user: TokenPayload, permission: Permission) -> dict[str, Any]:
    alarm = get_alarm_repository().get(alarm_id)
    if alarm is None:
        raise AppException(404, "报警记录不存在")
    require_home_access(alarm["home_id"], current_user, permission)
    return alarm
