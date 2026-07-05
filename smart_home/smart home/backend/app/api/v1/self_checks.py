from fastapi import APIRouter, Depends

from app.core.access import require_device_access
from app.core.deps import get_current_user
from app.core.permissions import Permission
from app.core.security import TokenPayload
from app.repositories.factory import (
    get_device_repository,
    get_operation_log_repository,
    get_self_check_repository,
)
from app.services.operation_log_service import OperationLogService
from app.services.self_check_service import SelfCheckService
from app.utils.response import success_response

router = APIRouter(tags=["设备自检"])


def get_self_check_service() -> SelfCheckService:
    return SelfCheckService(
        get_self_check_repository(),
        get_device_repository(),
        OperationLogService(get_operation_log_repository()),
    )


@router.post("/devices/{device_id}/self-check", summary="发起设备自检")
def start_self_check(device_id: int, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_device_access(device_id, current_user, Permission.DEVICE_MANAGE)
    record = get_self_check_service().start_self_check(device_id, current_user.user_id)
    return success_response(record)


@router.get("/devices/{device_id}/self-checks", summary="查询设备自检记录")
def list_self_checks(device_id: int, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_device_access(device_id, current_user, Permission.HOME_VIEW)
    records = get_self_check_service().list_self_checks(device_id)
    return success_response(records)
