from fastapi import APIRouter, Depends

from app.core.access import require_alarm_access, require_home_access
from app.core.deps import get_current_user
from app.core.permissions import Permission
from app.core.security import TokenPayload
from app.repositories.factory import get_alarm_repository, get_operation_log_repository
from app.schemas.alarm import AlarmProcessRequest
from app.services.alarm_service import AlarmService
from app.services.operation_log_service import OperationLogService
from app.utils.response import success_response

router = APIRouter(tags=["报警中心"])


def get_alarm_service() -> AlarmService:
    return AlarmService(
        get_alarm_repository(),
        OperationLogService(get_operation_log_repository()),
    )


@router.get("/homes/{home_id}/alarms", summary="查询报警列表")
def list_alarms(home_id: int, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_home_access(home_id, current_user, Permission.HOME_VIEW)
    alarms = get_alarm_service().list_alarms(home_id)
    return success_response(alarms)


@router.get("/alarms/{alarm_id}", summary="查询报警详情")
def get_alarm(alarm_id: int, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_alarm_access(alarm_id, current_user, Permission.HOME_VIEW)
    alarm = get_alarm_service().get_alarm_detail(alarm_id)
    return success_response(alarm)


@router.post("/alarms/{alarm_id}/confirm", summary="确认报警")
def confirm_alarm(
    alarm_id: int,
    payload: AlarmProcessRequest | None = None,
    current_user: TokenPayload = Depends(get_current_user),
) -> dict:
    require_alarm_access(alarm_id, current_user, Permission.ALARM_MANAGE)
    alarm = get_alarm_service().confirm_alarm(
        alarm_id,
        (payload or AlarmProcessRequest()).model_dump(),
        current_user.user_id,
    )
    return success_response(alarm)


@router.post("/alarms/{alarm_id}/process", summary="处理报警")
def process_alarm(alarm_id: int, payload: AlarmProcessRequest, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_alarm_access(alarm_id, current_user, Permission.ALARM_MANAGE)
    alarm = get_alarm_service().process_alarm(alarm_id, payload.model_dump(), current_user.user_id)
    return success_response(alarm)


@router.post("/alarms/{alarm_id}/resolve", summary="关闭报警")
def resolve_alarm(
    alarm_id: int,
    payload: AlarmProcessRequest | None = None,
    current_user: TokenPayload = Depends(get_current_user),
) -> dict:
    require_alarm_access(alarm_id, current_user, Permission.ALARM_MANAGE)
    alarm = get_alarm_service().resolve_alarm(
        alarm_id,
        (payload or AlarmProcessRequest()).model_dump(),
        current_user.user_id,
    )
    return success_response(alarm)


@router.post("/alarms/{alarm_id}/false-alarm", summary="标记误报")
def mark_false_alarm(
    alarm_id: int,
    payload: AlarmProcessRequest | None = None,
    current_user: TokenPayload = Depends(get_current_user),
) -> dict:
    require_alarm_access(alarm_id, current_user, Permission.ALARM_MANAGE)
    alarm = get_alarm_service().mark_false_alarm(
        alarm_id,
        (payload or AlarmProcessRequest()).model_dump(),
        current_user.user_id,
    )
    return success_response(alarm)
