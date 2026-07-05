from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.core.security import TokenPayload
from app.schemas.member import MemberApproveRequest, MemberApplyRequest, MemberInviteRequest, MemberPermissionRequest
from app.services.member_service import MemberService
from app.utils.response import success

router = APIRouter(prefix="/homes/{home_id}/members", tags=["成员管理"])


@router.post("/invite")
def invite_member(home_id: int, payload: MemberInviteRequest, current_user: TokenPayload = Depends(get_current_user)):
    data = MemberService().invite(home_id, current_user.user_id, payload.phone, payload.role, payload.expire_at)
    return success(data)


@router.post("/apply")
def apply_member(home_id: int, payload: MemberApplyRequest, current_user: TokenPayload = Depends(get_current_user)):
    data = MemberService().apply(home_id, current_user.user_id, payload.reason)
    return success(data)


@router.post("/{member_id}/accept")
def accept_invitation(home_id: int, member_id: int, current_user: TokenPayload = Depends(get_current_user)):
    data = MemberService().accept_invitation(home_id, member_id, current_user.user_id)
    return success(data)


@router.post("/{member_id}/approve")
def approve_member(home_id: int, member_id: int, payload: MemberApproveRequest, current_user: TokenPayload = Depends(get_current_user)):
    data = MemberService().approve(home_id, current_user.user_id, member_id, payload.approved, payload.role)
    return success(data)


@router.get("")
def list_members(home_id: int, current_user: TokenPayload = Depends(get_current_user)):
    return success(MemberService().list_members(home_id, current_user.user_id))


@router.put("/{member_id}/permission")
def update_permission(home_id: int, member_id: int, payload: MemberPermissionRequest, current_user: TokenPayload = Depends(get_current_user)):
    data = MemberService().update_permission(home_id, current_user.user_id, member_id, payload.role, payload.expire_at)
    return success(data)


@router.delete("/{member_id}")
def remove_member(home_id: int, member_id: int, current_user: TokenPayload = Depends(get_current_user)):
    return success(MemberService().remove(home_id, current_user.user_id, member_id))