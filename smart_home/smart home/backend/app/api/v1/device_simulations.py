from fastapi import APIRouter, Depends

from app.core.access import require_device_access
from app.core.deps import get_current_user
from app.core.permissions import Permission
from app.core.security import TokenPayload
from app.repositories.factory import (
    get_alarm_repository,
    get_device_repository,
    get_device_simulation_repository,
    get_operation_log_repository,
)
from app.schemas.device_simulation import DeviceSimulationCreate
from app.services.device_simulation_service import DeviceSimulationService
from app.services.operation_log_service import OperationLogService
from app.utils.response import success_response

router = APIRouter(tags=["设备模拟"])


def get_device_simulation_service() -> DeviceSimulationService:
    return DeviceSimulationService(
        get_device_simulation_repository(),
        get_device_repository(),
        get_alarm_repository(),
        OperationLogService(get_operation_log_repository()),
    )


@router.post("/devices/{device_id}/simulate", summary="模拟设备数据")
def create_simulation(device_id: int, payload: DeviceSimulationCreate, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_device_access(device_id, current_user, Permission.ALARM_MANAGE)
    record = get_device_simulation_service().create_simulation(device_id, payload.model_dump(), current_user.user_id)
    return success_response(record)


@router.get("/devices/{device_id}/simulations", summary="查询设备模拟记录")
def list_simulations(device_id: int, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_device_access(device_id, current_user, Permission.HOME_VIEW)
    records = get_device_simulation_service().list_simulations(device_id)
    return success_response(records)
