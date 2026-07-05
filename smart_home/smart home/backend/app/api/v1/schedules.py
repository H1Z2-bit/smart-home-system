from fastapi import APIRouter, Depends

from app.core.access import require_home_access, require_schedule_access
from app.core.deps import get_current_user
from app.core.permissions import Permission
from app.core.security import TokenPayload
from app.repositories.factory import (
    get_device_repository,
    get_operation_log_repository,
    get_schedule_repository,
)
from app.schemas.schedule import ScheduleCreate, ScheduleStatusUpdate, ScheduleUpdate
from app.services.operation_log_service import OperationLogService
from app.services.schedule_service import ScheduleService
from app.utils.response import success_response

router = APIRouter(tags=["定时任务"])


def get_schedule_service() -> ScheduleService:
    return ScheduleService(
        get_schedule_repository(),
        get_device_repository(),
        OperationLogService(get_operation_log_repository()),
    )


@router.post("/homes/{home_id}/schedules", summary="新增定时任务")
def create_schedule(home_id: int, payload: ScheduleCreate, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_home_access(home_id, current_user, Permission.AUTOMATION_MANAGE)
    task = get_schedule_service().create_schedule(home_id, payload.model_dump(), current_user.user_id)
    return success_response(task)


@router.get("/homes/{home_id}/schedules", summary="查询定时任务列表")
def list_schedules(home_id: int, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_home_access(home_id, current_user, Permission.HOME_VIEW)
    tasks = get_schedule_service().list_schedules(home_id)
    return success_response(tasks)


@router.put("/schedules/{task_id}", summary="修改定时任务")
def update_schedule(task_id: int, payload: ScheduleUpdate, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_schedule_access(task_id, current_user, Permission.AUTOMATION_MANAGE)
    task = get_schedule_service().update_schedule(task_id, payload.model_dump(exclude_unset=True), current_user.user_id)
    return success_response(task)


@router.put("/schedules/{task_id}/status", summary="启用或停用定时任务")
def update_schedule_status(task_id: int, payload: ScheduleStatusUpdate, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_schedule_access(task_id, current_user, Permission.AUTOMATION_MANAGE)
    task = get_schedule_service().update_schedule_status(task_id, payload.status, current_user.user_id)
    return success_response(task)


@router.delete("/schedules/{task_id}", summary="删除定时任务")
def delete_schedule(task_id: int, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_schedule_access(task_id, current_user, Permission.AUTOMATION_MANAGE)
    result = get_schedule_service().delete_schedule(task_id, current_user.user_id)
    return success_response(result, "删除定时任务成功")
