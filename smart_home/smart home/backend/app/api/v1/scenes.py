from fastapi import APIRouter, Depends

from app.core.access import require_home_access, require_scene_access
from app.core.deps import get_current_user
from app.core.permissions import Permission
from app.core.security import TokenPayload
from app.repositories.factory import (
    get_device_repository,
    get_operation_log_repository,
    get_scene_repository,
)
from app.schemas.scene import SceneCreate, SceneUpdate
from app.services.operation_log_service import OperationLogService
from app.services.scene_service import SceneService
from app.utils.response import success_response

router = APIRouter(tags=["情景模式"])


def get_scene_service() -> SceneService:
    return SceneService(
        get_scene_repository(),
        get_device_repository(),
        OperationLogService(get_operation_log_repository()),
    )


@router.post("/homes/{home_id}/scenes", summary="新增情景模式")
def create_scene(home_id: int, payload: SceneCreate, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_home_access(home_id, current_user, Permission.AUTOMATION_MANAGE)
    scene = get_scene_service().create_scene(home_id, payload.model_dump(), current_user.user_id)
    return success_response(scene)


@router.get("/homes/{home_id}/scenes", summary="查询情景模式列表")
def list_scenes(home_id: int, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_home_access(home_id, current_user, Permission.HOME_VIEW)
    scenes = get_scene_service().list_scenes(home_id)
    return success_response(scenes)


@router.put("/scenes/{scene_id}", summary="修改情景模式")
def update_scene(scene_id: int, payload: SceneUpdate, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_scene_access(scene_id, current_user, Permission.AUTOMATION_MANAGE)
    scene = get_scene_service().update_scene(scene_id, payload.model_dump(exclude_unset=True), current_user.user_id)
    return success_response(scene)


@router.delete("/scenes/{scene_id}", summary="删除情景模式")
def delete_scene(scene_id: int, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_scene_access(scene_id, current_user, Permission.AUTOMATION_MANAGE)
    result = get_scene_service().delete_scene(scene_id, current_user.user_id)
    return success_response(result, "删除情景模式成功")


@router.post("/scenes/{scene_id}/execute", summary="执行情景模式")
def execute_scene(scene_id: int, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_scene_access(scene_id, current_user, Permission.DEVICE_CONTROL)
    result = get_scene_service().execute_scene(scene_id, current_user.user_id)
    return success_response(result)
