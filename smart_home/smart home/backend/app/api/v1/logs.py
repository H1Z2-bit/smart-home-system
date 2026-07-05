from fastapi import APIRouter, Depends

from app.core.access import require_home_access
from app.core.deps import get_current_user
from app.core.permissions import Permission
from app.core.security import TokenPayload
from app.repositories.factory import get_operation_log_repository
from app.services.operation_log_service import OperationLogService
from app.utils.response import success_response

router = APIRouter(tags=["操作日志"])


def get_operation_log_service() -> OperationLogService:
    return OperationLogService(get_operation_log_repository())


@router.get("/homes/{home_id}/logs", summary="查询操作日志")
def list_logs(home_id: int, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_home_access(home_id, current_user, Permission.LOG_VIEW)
    logs = get_operation_log_service().list_logs(home_id)
    return success_response(logs)
