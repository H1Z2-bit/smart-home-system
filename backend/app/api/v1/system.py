from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.core.security import TokenPayload
from app.schemas.system_config import SystemConfigUpdateRequest
from app.services.system_config_service import SystemConfigService
from app.utils.response import success

router = APIRouter(prefix="/homes/{home_id}", tags=["系统配置与日志"])


@router.get("/system/config")
def get_config(home_id: int, current_user: TokenPayload = Depends(get_current_user)):
    return success(SystemConfigService().get_config(home_id, current_user.user_id))


@router.put("/system/config")
def update_config(home_id: int, payload: SystemConfigUpdateRequest, current_user: TokenPayload = Depends(get_current_user)):
    data = SystemConfigService().update_config(home_id, current_user.user_id, **payload.model_dump())
    return success(data)


@router.get("/logs")
def list_logs(home_id: int, current_user: TokenPayload = Depends(get_current_user)):
    return success(SystemConfigService().list_logs(home_id, current_user.user_id))