from fastapi import APIRouter, Depends

from app.core.access import require_home_access, require_linkage_access
from app.core.deps import get_current_user
from app.core.permissions import Permission
from app.core.security import TokenPayload
from app.repositories.factory import get_linkage_repository, get_operation_log_repository
from app.schemas.linkage import LinkageCreate, LinkageUpdate
from app.services.linkage_service import LinkageService
from app.services.operation_log_service import OperationLogService
from app.utils.response import success_response

router = APIRouter(tags=["联动规则"])


def get_linkage_service() -> LinkageService:
    return LinkageService(
        get_linkage_repository(),
        OperationLogService(get_operation_log_repository()),
    )


@router.post("/homes/{home_id}/linkages", summary="新增联动规则")
def create_rule(home_id: int, payload: LinkageCreate, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_home_access(home_id, current_user, Permission.AUTOMATION_MANAGE)
    rule = get_linkage_service().create_rule(home_id, payload.model_dump(), current_user.user_id)
    return success_response(rule)


@router.get("/homes/{home_id}/linkages", summary="查询联动规则列表")
def list_rules(home_id: int, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_home_access(home_id, current_user, Permission.HOME_VIEW)
    rules = get_linkage_service().list_rules(home_id)
    return success_response(rules)


@router.put("/linkages/{rule_id}", summary="修改联动规则")
def update_rule(rule_id: int, payload: LinkageUpdate, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_linkage_access(rule_id, current_user, Permission.AUTOMATION_MANAGE)
    rule = get_linkage_service().update_rule(rule_id, payload.model_dump(exclude_unset=True), current_user.user_id)
    return success_response(rule)


@router.delete("/linkages/{rule_id}", summary="删除联动规则")
def delete_rule(rule_id: int, current_user: TokenPayload = Depends(get_current_user)) -> dict:
    require_linkage_access(rule_id, current_user, Permission.AUTOMATION_MANAGE)
    result = get_linkage_service().delete_rule(rule_id, current_user.user_id)
    return success_response(result, "删除联动规则成功")
